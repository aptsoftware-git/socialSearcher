import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Avatar,
  Chip,
  Stack,
  IconButton,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableRow,
  TableCell,
  Divider,
  Link as MuiLink,
} from '@mui/material';
import {
  Close as CloseIcon,
  ThumbUp as ThumbUpIcon,
  Comment as CommentIcon,
  Share as ShareIcon,
  Visibility as ViewIcon,
  Verified as VerifiedIcon,
  Psychology as AnalyseIcon,
  OpenInNew as OpenInNewIcon,
  Facebook as FacebookIcon,
  Twitter as TwitterIcon,
  YouTube as YouTubeIcon,
  Instagram as InstagramIcon,
  Event as EventIcon,
} from '@mui/icons-material';
import { SocialFullContent, EventData } from '../types/events';
import { apiService } from '../services/api';
import { format, parseISO } from 'date-fns';

interface SocialContentModalProps {
  open: boolean;
  onClose: () => void;
  content: SocialFullContent | null;
  llmModel?: string;
  onCacheUpdate?: () => void;  // Callback to refresh cache status
}

const SocialContentModal: React.FC<SocialContentModalProps> = ({
  open,
  onClose,
  content,
  llmModel,
  onCacheUpdate,
}) => {
  // Helper function to proxy Instagram images through backend (fixes CORS issues)
  const getProxiedImageUrl = (url: string, platform: string): string => {
    if (platform === 'instagram' && url) {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'https://localhost:8000';
      return `${apiBaseUrl}/api/v1/proxy-image?url=${encodeURIComponent(url)}`;
    }
    return url;
  };
  const [analyzing, setAnalyzing] = useState(false);
  const [extractedEvent, setExtractedEvent] = useState<EventData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingCache, setLoadingCache] = useState(false);
  const [isCached, setIsCached] = useState(false);

  // Check for cached analysis when content changes or modal opens
  useEffect(() => {
    const checkCachedAnalysis = async () => {
      if (!content?.url || !open) return;
      
      setExtractedEvent(null);
      setError(null);
      setAnalyzing(false);
      setIsCached(false);
      setLoadingCache(true);

      try {
        // Check localStorage first for analyzed URLs
        const analyzedKey = `analyzed_${content.url}_${llmModel || 'default'}`;
        const cached = localStorage.getItem(analyzedKey);
        
        if (cached) {
          // We have a cached analysis, fetch it from backend
          const response = await apiService.analyseSocialContent({
            content: content,
            llm_model: llmModel,
          });

          if (response.status === 'success' && response.event) {
            setExtractedEvent(response.event);
            setIsCached(true);
            
            // Notify parent to refresh cache status since we loaded cached analysis
            if (onCacheUpdate) {
              onCacheUpdate();
            }
          }
        }
      } catch (err) {
        // Silently fail - user can still manually click "ANALYSE WITH AI"
        // console.debug('No cached analysis available', err);
      } finally {
        setLoadingCache(false);
      }
    };

    checkCachedAnalysis();
  }, [content, open, llmModel, onCacheUpdate]); // Check when content, modal state, or model changes

  if (!content) return null;

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'facebook':
        return <FacebookIcon />;
      case 'twitter':
      case 'x':
        return <TwitterIcon />;
      case 'youtube':
        return <YouTubeIcon />;
      case 'instagram':
        return <InstagramIcon />;
      default:
        return null;
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'facebook':
        return '#1877f2';
      case 'twitter':
      case 'x':
        return '#1da1f2';
      case 'youtube':
        return '#ff0000';
      case 'instagram':
        return '#e4405f';
      default:
        return '#999';
    }
  };

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'N/A';
    try {
      const date = parseISO(dateString);
      return format(date, 'PPP p'); // Format with time
    } catch {
      return dateString;
    }
  };

  const formatDateOnly = (dateString: string | undefined): string => {
    if (!dateString) return 'N/A';
    try {
      const date = parseISO(dateString);
      return format(date, 'PPP'); // Format without time
    } catch {
      return dateString;
    }
  };

  const formatPerpetratorType = (type: string | undefined): string => {
    if (!type) return '';
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatLocation = (): string => {
    if (!extractedEvent?.location) return 'N/A';
    const parts = [
      extractedEvent.location.venue,
      extractedEvent.location.city,
      extractedEvent.location.state,
      extractedEvent.location.country,
    ].filter(Boolean);
    return parts.length > 0 ? parts.join(', ') : 'N/A';
  };

  const getEventTypeColor = (type: string): 'error' | 'warning' | 'info' | 'success' => {
    const lowerType = type.toLowerCase();
    if (lowerType.includes('attack') || lowerType.includes('shooting') || lowerType.includes('bombing')) return 'error';
    if (lowerType.includes('riot') || lowerType.includes('violence')) return 'warning';
    if (lowerType.includes('protest') || lowerType.includes('demonstration')) return 'info';
    return 'success';
  };

  const handleAnalyse = async () => {
    setAnalyzing(true);
    setError(null);

    try {
      const response = await apiService.analyseSocialContent({
        content: content,
        llm_model: llmModel,
      });

      if (response.status === 'success' && response.event) {
        setExtractedEvent(response.event);
        setIsCached(true);
        
        // Store in localStorage that this URL has been analyzed
        const analyzedKey = `analyzed_${content.url}_${llmModel || 'default'}`;
        localStorage.setItem(analyzedKey, 'true');
        
        // Wait a moment for backend to update cache, then notify parent to refresh cache status
        if (onCacheUpdate) {
          // Small delay to ensure backend cache is updated
          setTimeout(() => {
            onCacheUpdate();
          }, 500);
        }
      } else {
        setError(response.error || 'Failed to extract event from content');
      }
    } catch (err) {
      console.error('Error analysing content:', err);
      setError(err instanceof Error ? err.message : 'Failed to analyse content');
    } finally {
      setAnalyzing(false);
    }
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="lg" 
      fullWidth
      scroll="paper"
      PaperProps={{
        sx: {
          minWidth: '600px',
          minHeight: '400px',
          maxWidth: '90vw',
          maxHeight: '90vh',
        }
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={1}>
            <Box sx={{ color: getPlatformColor(content.platform) }}>
              {getPlatformIcon(content.platform)}
            </Box>
            <Typography variant="h6" component="span" textTransform="capitalize">
              {content.platform} Post Details
            </Typography>
            {content.cached && (
              <Chip
                label="Cached"
                size="small"
                color="info"
                variant="outlined"
                sx={{ ml: 1 }}
              />
            )}
            {content.platform_data && 
             typeof content.platform_data === 'object' && 
             'is_from_playlist' in content.platform_data && 
             content.platform_data.is_from_playlist === true && (
              <Chip
                label="From Playlist"
                size="small"
                color="warning"
                variant="outlined"
                sx={{ ml: 1 }}
              />
            )}
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {/* Author Section */}
        <Box mb={3}>
          <Stack direction="row" spacing={2} alignItems="center">
            <Avatar
              src={getProxiedImageUrl(content.author.profile_picture || '', content.platform)}
              alt={content.author.name}
              sx={{ width: 56, height: 56 }}
            />
            <Box flex={1}>
              <Box display="flex" alignItems="center" gap={1}>
                <Typography variant="h6">
                  {content.author.name}
                </Typography>
                {content.author.verified && (
                  <VerifiedIcon color="primary" fontSize="small" />
                )}
              </Box>
              {content.author.username && (
                <Typography variant="body2" color="text.secondary">
                  @{content.author.username}
                </Typography>
              )}
              <Typography variant="caption" color="text.secondary">
                Posted: {formatDate(content.posted_at)}
              </Typography>
            </Box>
            <MuiLink
              href={content.url}
              target="_blank"
              rel="noopener noreferrer"
              underline="none"
            >
              <Button
                variant="outlined"
                size="small"
                endIcon={<OpenInNewIcon />}
              >
                Open Original
              </Button>
            </MuiLink>
          </Stack>
        </Box>

        <Divider />

        {/* Media Gallery - MOVED TO TOP */}
        {content.media && content.media.length > 0 && (
          <Box my={3} sx={{ display: 'flex', justifyContent: 'center' }}>
            <Box sx={{ width: '100%', maxWidth: '600px' }}>
              {/* <Typography variant="subtitle2" gutterBottom>
                Media ({content.media.length})
              </Typography> */}
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: content.media.length === 1 ? '1fr' : 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: 2,
                  width: '100%',
                }}
              >
                {content.media.map((media, index) => (
                <Box key={index} sx={{ width: '100%' }}>
                  {media.type === 'video' || content.platform.toLowerCase() === 'youtube' ? (
                    <Box
                      sx={{
                        position: 'relative',
                        width: '100%',
                        aspectRatio: '16 / 9',
                        maxHeight: '320px',
                        backgroundColor: '#000',
                        borderRadius: 1,
                        overflow: 'hidden',
                      }}
                    >
                      {content.platform.toLowerCase() === 'youtube' && content.url ? (
                        // For YouTube, extract video ID and embed the player
                        (() => {
                          // Try multiple methods to get video ID
                          let videoId: string | null = null;
                          
                          // Method 1: From platform_data (most reliable for playlists)
                          if (content.platform_data && 'video_id' in content.platform_data && typeof content.platform_data.video_id === 'string') {
                            videoId = content.platform_data.video_id;
                          }
                          // Method 2: Parse from URL
                          else if (content.url.includes('youtube.com/watch?v=')) {
                            videoId = new URL(content.url).searchParams.get('v');
                          }
                          // Method 3: youtu.be short URL
                          else if (content.url.includes('youtu.be/')) {
                            videoId = content.url.split('youtu.be/')[1]?.split('?')[0] || null;
                          }
                          
                          return videoId ? (
                            <iframe
                              src={`https://www.youtube.com/embed/${videoId}`}
                              title="YouTube video player"
                              frameBorder="0"
                              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                              allowFullScreen
                              style={{
                                position: 'absolute',
                                top: 0,
                                left: 0,
                                width: '100%',
                                height: '100%',
                                border: 'none',
                              }}
                            />
                          ) : (
                            <video
                              src={media.url}
                              poster={media.thumbnail_url}
                              controls
                              style={{
                                position: 'absolute',
                                top: 0,
                                left: 0,
                                width: '100%',
                                height: '100%',
                              }}
                            />
                          );
                        })()
                      ) : (
                        <video
                          src={media.url}
                          poster={media.thumbnail_url}
                          controls
                          style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                          }}
                        />
                      )}
                    </Box>
                  ) : (
                    <Box
                      sx={{
                        width: '100%',
                        borderRadius: 1,
                        overflow: 'hidden',
                      }}
                    >
                      <img
                        src={getProxiedImageUrl(media.url, content.platform)}
                        alt={`Media ${index + 1}`}
                        loading="lazy"
                        style={{
                          width: '100%',
                          height: 'auto',
                          maxHeight: '500px',
                          objectFit: 'contain',
                          display: 'block',
                        }}
                      />
                    </Box>
                  )}
                </Box>
              ))}
            </Box>
            </Box>
          </Box>
        )}

        {/* Content Section */}
        <Box my={3}>
          {content.title && (
            <Typography variant="h5" gutterBottom fontWeight="bold">
              {content.title}
            </Typography>
          )}
          {content.text && (
            <Typography variant="body1" paragraph whiteSpace="pre-wrap">
              {content.text}
            </Typography>
          )}
          {content.description && content.description !== content.text && (
            <Typography variant="body2" color="text.secondary" paragraph>
              {content.description}
            </Typography>
          )}
        </Box>

        <Divider />

        {/* Engagement Metrics */}
        <Box my={3}>
          <Typography variant="subtitle2" gutterBottom>
            Engagement
          </Typography>
          <Stack direction="row" spacing={2} flexWrap="wrap">
            {content.engagement.views > 0 && (
              <Chip
                icon={<ViewIcon />}
                label={`${formatNumber(content.engagement.views)} views`}
                variant="outlined"
              />
            )}
            {content.engagement.likes > 0 && (
              <Chip
                icon={<ThumbUpIcon />}
                label={`${formatNumber(content.engagement.likes)} likes`}
                variant="outlined"
              />
            )}
            {content.engagement.comments > 0 && (
              <Chip
                icon={<CommentIcon />}
                label={`${formatNumber(content.engagement.comments)} comments`}
                variant="outlined"
              />
            )}
            {content.engagement.shares > 0 && (
              <Chip
                icon={<ShareIcon />}
                label={`${formatNumber(content.engagement.shares)} shares`}
                variant="outlined"
              />
            )}
            {content.engagement.retweets !== undefined && content.engagement.retweets > 0 && (
              <Chip
                icon={<ShareIcon />}
                label={`${formatNumber(content.engagement.retweets)} retweets`}
                variant="outlined"
              />
            )}
          </Stack>
        </Box>

        {/* Analyse Button or Loading Cache */}
        {!extractedEvent && (
          <>
            <Divider />
            <Box my={3} textAlign="center">
              {loadingCache ? (
                <>
                  <CircularProgress size={24} />
                  <Typography variant="caption" display="block" mt={1} color="text.secondary">
                    Checking for cached analysis...
                  </Typography>
                </>
              ) : (
                <>
                  <Button
                    variant="contained"
                    color="primary"
                    size="large"
                    startIcon={analyzing ? <CircularProgress size={20} /> : <AnalyseIcon />}
                    onClick={handleAnalyse}
                    disabled={analyzing}
                  >
                    {analyzing ? 'Analysing with AI...' : 'Analyse with AI'}
                  </Button>
                  <Typography variant="caption" display="block" mt={1} color="text.secondary">
                    Extract event information using AI (Claude/Ollama)
                  </Typography>
                </>
              )}
            </Box>
          </>
        )}

        {/* Error Message */}
        {error && (
          <Alert severity="error" sx={{ my: 2 }}>
            {error}
          </Alert>
        )}

        {/* Extracted Event */}
        {extractedEvent && (
          <>
            <Divider />
            <Box my={3}>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <EventIcon color="primary" />
                Event Details
                {isCached && (
                  <Chip label="Cached" size="small" color="success" variant="outlined" sx={{ ml: 1 }} />
                )}
              </Typography>
              <Table size="small">
                <TableBody>
                  {/* Event Date */}
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold', width: '35%' }}>Event Date</TableCell>
                    <TableCell>{formatDateOnly(extractedEvent.event_date || extractedEvent.date)}</TableCell>
                  </TableRow>

                  {/* Event Time */}
                  {extractedEvent.event_time && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Event Time</TableCell>
                      <TableCell>{extractedEvent.event_time}</TableCell>
                    </TableRow>
                  )}

                  {/* Event Type */}
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Event Type</TableCell>
                    <TableCell>
                      <Chip
                        label={extractedEvent.event_type}
                        size="small"
                        color={getEventTypeColor(extractedEvent.event_type)}
                      />
                    </TableCell>
                  </TableRow>

                  {/* Event Sub-Type */}
                  {extractedEvent.event_sub_type && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Event Sub-Type</TableCell>
                      <TableCell>{extractedEvent.event_sub_type}</TableCell>
                    </TableRow>
                  )}

                  {/* Event Title */}
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Event Title</TableCell>
                    <TableCell>{extractedEvent.title}</TableCell>
                  </TableRow>

                  {/* Event Summary */}
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Event Summary</TableCell>
                    <TableCell>{extractedEvent.summary || 'N/A'}</TableCell>
                  </TableRow>

                  {/* Perpetrator */}
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Perpetrator</TableCell>
                    <TableCell>{extractedEvent.perpetrator || 'N/A'}</TableCell>
                  </TableRow>

                  {/* Perpetrator Type */}
                  {extractedEvent.perpetrator_type && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Perpetrator Type</TableCell>
                      <TableCell>{formatPerpetratorType(extractedEvent.perpetrator_type)}</TableCell>
                    </TableRow>
                  )}

                  {/* Location (Full) */}
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Location (Full)</TableCell>
                    <TableCell>{formatLocation()}</TableCell>
                  </TableRow>

                  {/* City/Town */}
                  {extractedEvent.location?.city && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>City/Town</TableCell>
                      <TableCell>{extractedEvent.location.city}</TableCell>
                    </TableRow>
                  )}

                  {/* State/Province */}
                  {extractedEvent.location?.state && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>State/Province</TableCell>
                      <TableCell>{extractedEvent.location.state}</TableCell>
                    </TableRow>
                  )}

                  {/* Country */}
                  {extractedEvent.location?.country && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Country</TableCell>
                      <TableCell>{extractedEvent.location.country}</TableCell>
                    </TableRow>
                  )}

                  {/* Individuals Involved */}
                  {extractedEvent.participants && extractedEvent.participants.length > 0 && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Individuals Involved</TableCell>
                      <TableCell>{extractedEvent.participants.join(', ')}</TableCell>
                    </TableRow>
                  )}

                  {/* Organizations Involved */}
                  {extractedEvent.organizations && extractedEvent.organizations.length > 0 && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Organizations Involved</TableCell>
                      <TableCell>{extractedEvent.organizations.join(', ')}</TableCell>
                    </TableRow>
                  )}

                  {/* Casualties */}
                  {extractedEvent.casualties && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Casualties</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 2 }}>
                          {extractedEvent.casualties.killed !== undefined && (
                            <Chip label={`Killed: ${extractedEvent.casualties.killed}`} size="small" color="error" />
                          )}
                          {extractedEvent.casualties.injured !== undefined && (
                            <Chip label={`Injured: ${extractedEvent.casualties.injured}`} size="small" color="warning" />
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  )}

                  {/* Source Name */}
                  {extractedEvent.source_name && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Source Name</TableCell>
                      <TableCell>{extractedEvent.source_name}</TableCell>
                    </TableRow>
                  )}

                  {/* Source URL */}
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Source URL</TableCell>
                    <TableCell>
                      {(extractedEvent.source_url || extractedEvent.url) ? (
                        <MuiLink href={extractedEvent.source_url || extractedEvent.url} target="_blank" rel="noopener noreferrer">
                          {extractedEvent.source_url || extractedEvent.url}
                        </MuiLink>
                      ) : (
                        'N/A'
                      )}
                    </TableCell>
                  </TableRow>

                  {/* Publication Date */}
                  {extractedEvent.article_published_date && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Publication Date</TableCell>
                      <TableCell>{formatDate(extractedEvent.article_published_date)}</TableCell>
                    </TableRow>
                  )}

                  {/* Extraction Confidence */}
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Extraction Confidence</TableCell>
                    <TableCell>
                      <Chip
                        label={`${(extractedEvent.confidence * 100).toFixed(0)}%`}
                        size="small"
                        color={extractedEvent.confidence >= 0.8 ? 'success' : extractedEvent.confidence >= 0.6 ? 'warning' : 'error'}
                      />
                    </TableCell>
                  </TableRow>

                  {/* Collection Timestamp */}
                  {extractedEvent.collection_timestamp && (
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Collection Timestamp</TableCell>
                      <TableCell>{formatDate(extractedEvent.collection_timestamp)}</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </Box>
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} color="inherit">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SocialContentModal;
