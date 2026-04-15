import { useState, useEffect } from 'react';
import { Container, CssBaseline, ThemeProvider, createTheme, AppBar, Toolbar, Typography, Box } from '@mui/material';
import SearchForm from './components/SearchForm';
import EventList from './components/EventList';
import ProgressBar from './components/ProgressBar';
import LLMConfigDropdown from './components/LLMConfigDropdown';
import SocialResultsPanel from './components/SocialResultsPanel';
import Login from './components/Login';
import AdminDashboard from './components/AdminDashboard';
import ProfileMenu from './components/ProfileMenu';
import SearchQuotaBar from './components/SearchQuotaBar';
import { EventData, ProgressUpdate, SocialSearchResult } from './types/events';
import { streamService } from './services/streamService';
import { apiService } from './services/api';
import logoImage from './assets/aptvigilosint.webp';
import makeInIndiaLogo from './assets/Make_In_India.png';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  company?: string;
  profile_image_url?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login?: string;
}

function App() {
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // Search state
  const [events, setEvents] = useState<EventData[]>([]);
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [searchSummary, setSearchSummary] = useState<{ message: string; total_events: number } | null>(null);
  const [socialResults, setSocialResults] = useState<SocialSearchResult[]>([]);
  const [socialSearchQuery, setSocialSearchQuery] = useState<string>('');
  const [socialSearchSites, setSocialSearchSites] = useState<string[]>([]);
  const [socialSearchCounts, setSocialSearchCounts] = useState<{
    total: number;
    youtube: number;
    twitter: number;
    facebook: number;
    instagram: number;
    google: number;
  } | undefined>(undefined);
  
  // Track which platforms have no more results available
  const [platformsExhausted, setPlatformsExhausted] = useState<{
    youtube: boolean;
    twitter: boolean;
    facebook: boolean;
    instagram: boolean;
    google: boolean;
  }>({
    youtube: false,
    twitter: false,
    facebook: false,
    instagram: false,
    google: false,
  });

  // Check authentication on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setToken(storedToken);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Failed to parse stored user:', error);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
      }
    }
  }, []);

  const handleLoginSuccess = (loggedInUser: User, authToken: string) => {
    setUser(loggedInUser);
    setToken(authToken);
    setIsAuthenticated(true);
  };

  const handleUserUpdate = (updatedUser: User) => {
    setUser(updatedUser);
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  // Helper function to get display name (company > full_name > username)
  const getDisplayName = () => {
    if (!user) return '';
    if (user.company) return user.company;
    if (user.full_name) return user.full_name;
    return user.username;
  };

  const handleSearchStart = () => {
    // Reset state
    setEvents([]);
    setProgress(null);
    setSearchSummary(null);
    setIsStreaming(true);
    setSocialResults([]);
    setSocialSearchQuery('');
    setSocialSearchSites([]);
    setSocialSearchCounts(undefined);
  };

  const handleSocialSearchResults = (
    results: SocialSearchResult[], 
    query: string, 
    sites: string[],
    counts?: {
      total: number;
      youtube: number;
      twitter: number;
      facebook: number;
      instagram: number;
      google: number;
    }
  ) => {
    setSocialResults(results);
    setSocialSearchQuery(query);
    setSocialSearchSites(sites);
    setSocialSearchCounts(counts);
    
    // Reset exhausted platforms state for new search
    setPlatformsExhausted({
      youtube: false,
      twitter: false,
      facebook: false,
      instagram: false,
      google: false,
    });
  };

  const handleLoadMoreResults = async (platform: string) => {
    if (!socialSearchQuery) return;
    
    try {
      // Map platform name to site URL
      const platformMap: {[key: string]: string} = {
        'youtube': 'youtube.com',
        'twitter': 'x.com',
        'facebook': 'facebook.com',
        'instagram': 'instagram.com',
        'google': 'google.com'
      };
      
      const siteUrl = platformMap[platform];
      if (!siteUrl) return;
      
      // Count current results for this platform
      const currentPlatformResults = socialResults.filter((r: SocialSearchResult) => 
        r.source_site.toLowerCase().includes(platform) || 
        r.display_link.toLowerCase().includes(platform) ||
        (platform === 'twitter' && (r.source_site.toLowerCase().includes('x.com') || r.display_link.toLowerCase().includes('x.com')))
      );
      
      const currentCount = currentPlatformResults.length;
      const nextStartIndex = currentCount + 1; // Google CSE uses 1-based indexing
      
      // Check if we've reached the maximum limit (Google CSE allows start_index 1-91)
      if (nextStartIndex > 91) {
        console.log(`[${platform}] Reached maximum limit (start_index would be ${nextStartIndex}, max is 91)`);
        setPlatformsExhausted(prev => ({
          ...prev,
          [platform]: true
        }));
        alert('Maximum result limit reached for this platform. Google Custom Search API allows up to 100 results per search.');
        return;
      }
      
      console.log(`[${platform}] Current loaded results: ${currentCount}, requesting from index: ${nextStartIndex}`);
      console.log(`[${platform}] Requesting from site: ${siteUrl}`);
      console.log(`[${platform}] Current platformsExhausted state:`, platformsExhausted);
      
      // Fetch next 10 results for this platform only
      const newResults = await apiService.socialSearch(socialSearchQuery, [siteUrl], 10, nextStartIndex);
      
      console.log(`[${platform}] API Response - total_results: ${newResults.total_results}, results.length: ${newResults.results.length}`);
      
      // Check if API returned any results at all
      if (newResults.results.length === 0) {
        // API returned no results - mark this platform as exhausted
        console.log(`[${platform}] No more results available from API (start_index: ${nextStartIndex})`);
        setPlatformsExhausted(prev => ({
          ...prev,
          [platform]: true
        }));
        return;
      }
      
      // API returned results - now filter out duplicates
      const existingUrls = new Set(socialResults.map((r: SocialSearchResult) => r.link));
      const uniqueNewResults = newResults.results.filter((r: SocialSearchResult) => !existingUrls.has(r.link));
      
      // Add unique results if any
      if (uniqueNewResults.length > 0) {
        console.log(`[${platform}] Added ${uniqueNewResults.length} new unique results`);
        setSocialResults([...socialResults, ...uniqueNewResults]);
      } else {
        // All results were duplicates - mark as exhausted
        console.log(`[${platform}] All ${newResults.results.length} results were duplicates, marking as exhausted`);
        setPlatformsExhausted(prev => ({
          ...prev,
          [platform]: true
        }));
      }
    } catch (error) {
      console.error(`[${platform}] Load More failed:`, error);
      
      // Extract error message from axios error response
      let errorMessage = 'Failed to load more results';
      if (error && typeof error === 'object') {
        const axiosError = error as any;
        if (axiosError.response?.data?.detail) {
          errorMessage = axiosError.response.data.detail;
        } else if (axiosError.response?.status === 422) {
          // Validation error - likely hit the start_index limit
          errorMessage = 'Maximum result limit reached for this platform. Google Custom Search API allows up to 100 results per search.';
          // Mark platform as exhausted
          setPlatformsExhausted(prev => ({
            ...prev,
            [platform]: true
          }));
        } else if (axiosError.response?.status === 429) {
          errorMessage = 'Search limit exceeded. Daily quota has been reached. Please try again tomorrow.';
        } else if (axiosError.message) {
          errorMessage = axiosError.message;
        }
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      // Display error to user via alert
      alert(errorMessage);
    }
  };

  const handleProgress = (progressUpdate: ProgressUpdate) => {
    setProgress(progressUpdate);
  };

  const handleEventReceived = (event: EventData) => {
    // Add event to list immediately
    setEvents((prev) => [...prev, event]);
  };

  const handleSearchComplete = (summary: { message: string; total_events: number }) => {
    setIsStreaming(false);
    setProgress(null);
    setSearchSummary(summary);
  };

  const handleError = (error: string) => {
    console.error('Search error:', error);
    setIsStreaming(false);
    setProgress(null);
  };

  const handleCancel = async () => {
    if (window.confirm('Are you sure you want to cancel the search? Already extracted events will be kept.')) {
      try {
        await streamService.cancel();
        setIsStreaming(false);
        setProgress(null);
        
        // Reset SearchForm state
        handleSearchComplete({
          message: `Search cancelled. ${events.length} event(s) extracted.`,
          total_events: events.length
        });
      } catch (error) {
        console.error('Cancel error:', error);
        setIsStreaming(false);
        setProgress(null);
        handleSearchComplete({
          message: `Search cancelled. ${events.length} event(s) extracted.`,
          total_events: events.length
        });
      }
    }
  };

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Login onLoginSuccess={handleLoginSuccess} />
      </ThemeProvider>
    );
  }

  // Show admin dashboard for admin users
  if (user?.is_admin) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AdminDashboard token={token!} onLogout={handleLogout} />
      </ThemeProvider>
    );
  }

  // Show main search interface for regular users
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {/* App Bar */}
        <AppBar position="static">
          <Toolbar>
            <Box
              component="img"
              src={logoImage}
              alt="Logo"
              sx={{ height: 52, mr: 2 }}
            />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              <Box component="span" sx={{ fontWeight: 'bold' }}>Apt Vigil</Box> - AI based customized web scrapper
            </Typography>
            <Typography variant="body2" sx={{ mr: 1 }}>
              {getDisplayName()}
            </Typography>
            {user && <ProfileMenu user={user} onUserUpdate={handleUserUpdate} />}
            <LLMConfigDropdown />
            <SearchQuotaBar token={token!} />
            <Box sx={{ ml: 2 }}>
              <Typography 
                variant="body2" 
                sx={{ cursor: 'pointer', textDecoration: 'underline' }}
                onClick={handleLogout}
              >
                Logout
              </Typography>
            </Box>
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Box sx={{ mt: 4, mb: 4, flex: 1, width: '100%' }}>
          {/* Search Form - Centered */}
          <Container maxWidth="lg" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
            <SearchForm 
              onSearchStart={handleSearchStart}
              onProgress={handleProgress}
              onEventReceived={handleEventReceived}
              onSearchComplete={handleSearchComplete}
              onError={handleError}
              onSocialResults={handleSocialSearchResults}
            />
          </Container>

          {/* Social Results Panel */}
          {socialResults.length > 0 && (
            <Container maxWidth="lg" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
              <SocialResultsPanel 
                results={socialResults}
                query={socialSearchQuery}
                sites={socialSearchSites}
                counts={socialSearchCounts}
                onLoadMore={handleLoadMoreResults}
                platformsExhausted={platformsExhausted}
              />
            </Container>
          )}

          {/* Progress Bar */}
          {isStreaming && progress && (
            <Container maxWidth="lg" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
              <ProgressBar progress={progress} onCancel={handleCancel} />
            </Container>
          )}

          {/* Search Summary */}
          {searchSummary && (
            <Container maxWidth="lg" sx={{ px: { xs: 2, sm: 3, md: 4 }, mb: 2 }}>
              <Typography variant="body1" color="success.main">
                ✅ {searchSummary.message}
              </Typography>
            </Container>
          )}
          
          {/* Event List - Full Width - Shows events as they arrive */}
          <EventList events={events} />
        </Box>

        {/* Footer */}
        <Box component="footer" sx={{ py: 2, px: 1.5, mt: 'auto', backgroundColor: (theme) => theme.palette.grey[200] }}>
          <Container maxWidth="xl">
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
              {/* Make in India Logo - Absolute Left */}
              <Box
                component="img"
                src={makeInIndiaLogo}
                alt="Make in India"
                sx={{ 
                  height: 32,
                  position: 'absolute',
                  left: 0
                }}
              />
              
              {/* Developer Info - Centered */}
              <Typography variant="caption" color="text.secondary" align="center">
                Developed by Apt Software Avenues Pvt. Ltd. (a Defender Framework tool)
              </Typography>
            </Box>
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;