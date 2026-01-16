import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  MenuItem,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  ListSubheader,
  Collapse,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import { Search as SearchIcon, ExpandMore as ExpandMoreIcon } from '@mui/icons-material';
import { EventType, SearchQuery, ProgressUpdate, EventData, SocialSearchResult } from '../types/events';

interface SearchFormProps {
  onSearchStart?: () => void;
  onProgress?: (progress: ProgressUpdate) => void;
  onEventReceived?: (event: EventData) => void;
  onSearchComplete?: (summary: { message: string; total_events: number }) => void;
  onError?: (error: string) => void;
  onSocialResults?: (results: SocialSearchResult[], query: string, sites: string[]) => void;
}

// Helper function to get user-friendly event type labels
const getEventTypeLabel = (type: EventType): string => {
  const labels: Record<EventType, string> = {
    // Violence & Security Events
    [EventType.PROTEST]: 'Protest',
    [EventType.DEMONSTRATION]: 'Demonstration',
    [EventType.ATTACK]: 'Attack',
    [EventType.EXPLOSION]: 'Explosion',
    [EventType.BOMBING]: 'Bombing',
    [EventType.SHOOTING]: 'Shooting',
    [EventType.THEFT]: 'Theft',
    [EventType.KIDNAPPING]: 'Kidnapping',

    // Cyber Events
    [EventType.CYBER_ATTACK]: 'Cyber Attack',
    [EventType.CYBER_INCIDENT]: 'Cyber Incident',
    [EventType.DATA_BREACH]: 'Data Breach',

    // Meetings & Conferences
    [EventType.CONFERENCE]: 'Conference',
    [EventType.MEETING]: 'Meeting',
    [EventType.SUMMIT]: 'Summit',

    // Disasters & Accidents
    [EventType.ACCIDENT]: 'Accident',
    [EventType.NATURAL_DISASTER]: 'Natural Disaster',

    // Political & Military
    [EventType.ELECTION]: 'Election',
    [EventType.POLITICAL_EVENT]: 'Political Event',
    [EventType.MILITARY_OPERATION]: 'Military Operation',

    // Crisis Events
    [EventType.TERRORIST_ACTIVITY]: 'Terrorist Activity',
    [EventType.CIVIL_UNREST]: 'Civil Unrest',
    [EventType.HUMANITARIAN_CRISIS]: 'Humanitarian Crisis',

    // Other
    [EventType.OTHER]: 'Other',
  };
  return labels[type] || 'Unknown';
};

const eventTypeCategories: Record<string, EventType[]> = {
  'Violence & Security Events': [
    EventType.PROTEST,
    EventType.DEMONSTRATION,
    EventType.ATTACK,
    EventType.EXPLOSION,
    EventType.BOMBING,
    EventType.SHOOTING,
    EventType.THEFT,
    EventType.KIDNAPPING,
  ],
  'Cyber Events': [
    EventType.CYBER_ATTACK,
    EventType.CYBER_INCIDENT,
    EventType.DATA_BREACH,
  ],
  'Meetings & Conferences': [
    EventType.CONFERENCE,
    EventType.MEETING,
    EventType.SUMMIT,
  ],
  'Disasters & Accidents': [
    EventType.ACCIDENT,
    EventType.NATURAL_DISASTER,
  ],
  'Political & Military': [
    EventType.ELECTION,
    EventType.POLITICAL_EVENT,
    EventType.MILITARY_OPERATION,
  ],
  'Crisis Events': [
    EventType.TERRORIST_ACTIVITY,
    EventType.CIVIL_UNREST,
    EventType.HUMANITARIAN_CRISIS,
  ],
  'Other': [
    EventType.OTHER,
  ],
};

const SearchForm: React.FC<SearchFormProps> = ({ 
  onSearchStart, 
  onProgress, 
  onEventReceived, 
  onSearchComplete,
  onError,
  onSocialResults
}) => {
  const [formData, setFormData] = useState<SearchQuery>({
    phrase: '',
    location: '',
    event_type: undefined,
    date_from: '',
    date_to: '',
    use_social_search: true,  // Always true - checkbox UI is commented out
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false); // Advanced search options toggle
  const [platformWarning, setPlatformWarning] = useState<string | null>(null); // Platform selection warning
  
  // Platform selection state
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([
    'youtube.com', 'x.com', 'facebook.com', 'instagram.com', 'google.com'
  ]);
  
  const allPlatforms = [
    { id: 'youtube.com', label: 'YouTube' },
    { id: 'x.com', label: 'Twitter/X' },
    { id: 'facebook.com', label: 'Facebook' },
    { id: 'instagram.com', label: 'Instagram' },
    { id: 'google.com', label: 'Google' },
  ];

  const handleChange = (field: keyof SearchQuery) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.value;
    setFormData((prev) => ({
      ...prev,
      [field]: value || undefined,
    }));
  };

  // Platform selection handlers
  const handlePlatformToggle = (platformId: string) => {
    setSelectedPlatforms((prev) => {
      if (prev.includes(platformId)) {
        const newPlatforms = prev.filter((p) => p !== platformId);
        // Ensure at least one platform is selected
        if (newPlatforms.length === 0) {
          setPlatformWarning('At least one platform must be selected for searching');
          // Auto-dismiss after 5 seconds
          setTimeout(() => {
            setPlatformWarning(null);
          }, 5000);
          return prev; // Keep the current selection
        }
        return newPlatforms;
      } else {
        return [...prev, platformId];
      }
    });
  };

  const handleSelectAll = () => {
    const allPlatformIds = allPlatforms.map((p) => p.id);
    if (selectedPlatforms.length === allPlatformIds.length) {
      // All selected, keep at least one (don't deselect all)
      setSelectedPlatforms([allPlatformIds[0]]);
    } else {
      // Not all selected, select all
      setSelectedPlatforms(allPlatformIds);
    }
  };

  const isAllSelected = selectedPlatforms.length === allPlatforms.length;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    // Validation
    if (!formData.phrase.trim()) {
      setError('Please enter a search phrase');
      return;
    }

    // Platform validation
    if (selectedPlatforms.length === 0) {
      setError('Please select at least one platform');
      return;
    }

    // Date validation
    if (formData.date_from && formData.date_to) {
      const fromDate = new Date(formData.date_from);
      const toDate = new Date(formData.date_to);
      if (fromDate > toDate) {
        setError('Start date must be before end date');
        return;
      }
    }

    try {
      setLoading(true);
      if (onSearchStart) {
        onSearchStart();
      }

      // If social search is enabled, ONLY call social search (for testing)
      if (formData.use_social_search) {
        try {
          const { apiService } = await import('../services/api');
          
          // Enhance search phrase with location, event type, and date context
          // Build a natural, search-engine friendly query
          let enhancedQuery = formData.phrase;
          
          // Add event type first (more natural: "protest in Kolkata" vs "Kolkata protest")
          if (formData.event_type) {
            const eventTypeLabel = getEventTypeLabel(formData.event_type).toLowerCase();
            // Check if phrase already contains the event type
            if (!enhancedQuery.toLowerCase().includes(eventTypeLabel)) {
              enhancedQuery = `${eventTypeLabel} ${enhancedQuery}`;
            }
          }
          
          // Add location with preposition "in" for natural language
          if (formData.location?.trim()) {
            const location = formData.location.trim();
            // Check if location is already in the phrase
            if (!enhancedQuery.toLowerCase().includes(location.toLowerCase())) {
              enhancedQuery = `${enhancedQuery} in ${location}`;
            }
          }
          
          // Add date context in a natural way
          if (formData.date_from || formData.date_to) {
            const formatDate = (dateStr: string) => {
              const date = new Date(dateStr);
              return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
            };
            
            if (formData.date_from && formData.date_to) {
              // Both dates specified
              const fromDate = new Date(formData.date_from);
              const toDate = new Date(formData.date_to);
              const fromStr = formatDate(formData.date_from);
              const toStr = formatDate(formData.date_to);
              
              // Check if same month and year
              if (fromStr === toStr) {
                enhancedQuery = `${enhancedQuery} ${fromStr}`;
              } else if (fromDate.getFullYear() === toDate.getFullYear()) {
                // Same year, different months: "December 2025 to January 2026" → "December-January 2026"
                const fromMonth = fromDate.toLocaleDateString('en-US', { month: 'long' });
                const toMonth = toDate.toLocaleDateString('en-US', { month: 'long' });
                enhancedQuery = `${enhancedQuery} ${fromMonth}-${toMonth} ${toDate.getFullYear()}`;
              } else {
                // Different years
                enhancedQuery = `${enhancedQuery} ${fromStr} to ${toStr}`;
              }
            } else if (formData.date_from) {
              // Only from date: "since January 2025"
              enhancedQuery = `${enhancedQuery} since ${formatDate(formData.date_from)}`;
            } else if (formData.date_to) {
              // Only to date: "until January 2025"
              enhancedQuery = `${enhancedQuery} until ${formatDate(formData.date_to)}`;
            }
          } else {
            // No date specified - add "latest" or "recent" for more relevant results
            enhancedQuery = `${enhancedQuery} latest`;
          }
          
          console.log(`Enhanced query: "${enhancedQuery}" (original: "${formData.phrase}")`);
          console.log(`Selected platforms: ${selectedPlatforms.join(', ')}`);
          
          const socialResults = await apiService.socialSearch(enhancedQuery, selectedPlatforms);
          
          // Pass results to parent component for display
          if (onSocialResults) {
            onSocialResults(socialResults.results, socialResults.query, socialResults.sites);
          }
          
          // Show completion message
          setLoading(false);
          if (onSearchComplete) {
            // Create platform labels for display
            const platformLabels = selectedPlatforms.map(site => {
              const platform = allPlatforms.find(p => p.id === site);
              return platform ? platform.label : site;
            }).join(', ');
            
            onSearchComplete({
              message: `Social search completed. Found ${socialResults.total_results} results from ${platformLabels}`,
              total_events: socialResults.total_results,
            });
          }
          
          // Exit early - don't run regular search
          return;
          
        } catch (socialError) {
          console.error('Social search failed:', socialError);
          setLoading(false);
          const errorMessage = socialError instanceof Error ? socialError.message : 'Social search failed';
          setError(errorMessage);
          if (onError) {
            onError(errorMessage);
          }
          return;
        }
      }

      // Only run regular streaming search if social search is disabled
      const { streamService } = await import('../services/streamService');
      
      // Start streaming search (regular search)
      streamService.startStreaming(formData, {
        onProgress: (progress) => {
          if (onProgress) {
            onProgress(progress);
          }
        },
        onEvent: (eventData) => {
          if (onEventReceived) {
            onEventReceived(eventData);
          }
        },
        onComplete: (summary) => {
          setLoading(false);
          if (onSearchComplete) {
            onSearchComplete(summary);
          }
        },
        onCancelled: (summary) => {
          setLoading(false);
          if (onSearchComplete) {
            onSearchComplete(summary);
          }
        },
        onError: (errorMsg) => {
          setLoading(false);
          setError(errorMsg);
          if (onError) {
            onError(errorMsg);
          }
        },
      });
    } catch (err) {
      console.error('Search error:', err);
      const errorMessage = err instanceof Error ? err.message : 'An error occurred while searching. Please try again.';
      setError(errorMessage);
      setLoading(false);
      if (onError) {
        onError(errorMessage);
      }
    }
  };

  const handleReset = () => {
    setFormData({
      phrase: '',
      location: '',
      event_type: undefined,
      date_from: '',
      date_to: '',
      use_social_search: true,  // Always true - checkbox UI is commented out
    });
    // Reset platform selection to all
    setSelectedPlatforms(['youtube.com', 'x.com', 'facebook.com', 'instagram.com', 'google.com']);
    setError(null);
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
      <Box sx={{ width: '100%', maxWidth: { xs: '100%', md: '66.666%' } }}>
        {/* Search Form */}
        <Paper elevation={3} sx={{ p: 3, mb: 3, width: '100%' }}>
          <Typography variant="h5" gutterBottom>
            Search for Events
          </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          {/* Search Phrase */}
          <Grid size={{ xs: 12 }}>
            <TextField
              fullWidth
              required
              label="Search Phrase"
              placeholder="e.g., AI, Machine Learning, Cybersecurity"
              value={formData.phrase}
              onChange={handleChange('phrase')}
              disabled={loading}
              helperText="Enter keywords to search for relevant events"
            />
          </Grid>

          {/* Advanced Search Options Toggle */}
          <Grid size={{ xs: 12 }}>
            <Button
              onClick={() => setShowAdvanced(!showAdvanced)}
              startIcon={
                <ExpandMoreIcon
                  sx={{
                    transform: showAdvanced ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.3s',
                  }}
                />
              }
              sx={{ 
                textTransform: 'none',
                color: 'text.secondary',
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            >
              Custom Search Options
            </Button>
          </Grid>

          {/* Advanced Search Fields - Collapsible */}
          <Grid size={{ xs: 12 }}>
            <Collapse in={showAdvanced}>
              <Grid container spacing={2}>
                {/* Location */}
                <Grid size={{ xs: 12, md: 6 }}>
                  <TextField
                    fullWidth
                    label="Location (Optional)"
                    placeholder="e.g., New York, London, Online"
                    value={formData.location}
                    onChange={handleChange('location')}
                    disabled={loading}
                    helperText="City, state, country, or 'Online'"
                  />
                </Grid>

                {/* Event Type */}
                <Grid size={{ xs: 12, md: 6 }}>
                  <TextField
                    fullWidth
                    select
                    label="Event Type (Optional)"
                    value={formData.event_type || ''}
                    onChange={handleChange('event_type')}
                    disabled={loading}
                    helperText="Filter by event type"
                  >
                    <MenuItem value="">All Types</MenuItem>
                    {Object.entries(eventTypeCategories).map(([category, types]) => [
                      <ListSubheader key={category}>{category}</ListSubheader>,
                      ...types.map((type) => (
                        <MenuItem key={type} value={type}>
                          {getEventTypeLabel(type)}
                        </MenuItem>
                      ))
                    ])}
                  </TextField>
                </Grid>

                {/* Date From */}
                <Grid size={{ xs: 12, md: 6 }}>
                  <TextField
                    fullWidth
                    type="date"
                    label="Start Date (Optional)"
                    value={formData.date_from}
                    onChange={handleChange('date_from')}
                    disabled={loading}
                    InputLabelProps={{ shrink: true }}
                    helperText="Filter events from this date"
                  />
                </Grid>

                {/* Date To */}
                <Grid size={{ xs: 12, md: 6 }}>
                  <TextField
                    fullWidth
                    type="date"
                    label="End Date (Optional)"
                    value={formData.date_to}
                    onChange={handleChange('date_to')}
                    disabled={loading}
                    InputLabelProps={{ shrink: true }}
                    helperText="Filter events until this date"
                  />
                </Grid>

                
                {/* Platform Selection */}
                <Grid size={{ xs: 12 }}>
                  <Typography variant="subtitle2" gutterBottom sx={{ mt: 2, mb: 1 }}>
                    Select Platforms:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {/* All Checkbox */}
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={isAllSelected}
                          onChange={handleSelectAll}
                          disabled={loading}
                          color="primary"
                        />
                      }
                      label="All"
                      sx={{ minWidth: '80px', mr: 0.5 }}
                    />
                    
                    {/* Individual Platform Checkboxes */}
                    {allPlatforms.map((platform) => (
                      <FormControlLabel
                        key={platform.id}
                        control={
                          <Checkbox
                            checked={selectedPlatforms.includes(platform.id)}
                            onChange={() => handlePlatformToggle(platform.id)}
                            disabled={loading}
                            color="primary"
                          />
                        }
                        label={platform.label}
                        sx={{ minWidth: '120px', mr: 0.5 }}
                      />
                    ))}
                  </Box>
                  {platformWarning && (
                    <Alert severity="warning" sx={{ mt: 1, mb: 0.5 }}>
                      {platformWarning}
                    </Alert>
                  )}
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                    {selectedPlatforms.length} platform{selectedPlatforms.length !== 1 ? 's' : ''} selected
                  </Typography>
                </Grid>
              </Grid>
            </Collapse>
          </Grid>

          {/* Social Search Checkbox - COMMENTED OUT (use_social_search is always true) */}
          {/* Future: May need to re-enable this option */}
          {/* <Grid size={{ xs: 12 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.use_social_search || false}
                  onChange={(e) => setFormData(prev => ({ ...prev, use_social_search: e.target.checked }))}
                  disabled={loading}
                  color="primary"
                />
              }
              label="Use Social Media Search ONLY (YouTube, Twitter/X, Facebook, Instagram)"
            />
            <Typography variant="caption" display="block" color="text.secondary" sx={{ ml: 4, mt: -0.5 }}>
              When checked: Uses ONLY YouTube, Twitter/X, Facebook, Instagram Search (regular search is disabled)
            </Typography>
            <Typography variant="caption" display="block" color="warning.main" sx={{ ml: 4, mt: 0.5 }}>
              Regular streaming search will be skipped when this is enabled
            </Typography>
          </Grid> */}

          {/* Action Buttons */}
          <Grid size={{ xs: 12 }}>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                type="button"
                variant="outlined"
                onClick={handleReset}
                disabled={loading}
              >
                Reset
              </Button>
              <Button
                type="submit"
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                disabled={loading}
              >
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Box>

      {loading && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Searching and analyzing events... This may take a minute.
          </Typography>
        </Box>
      )}
        </Paper>
      </Box>
    </Box>
  );
};

export default SearchForm;
