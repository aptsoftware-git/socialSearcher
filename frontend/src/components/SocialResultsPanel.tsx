import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Link,
  Chip,
  Stack,
  Alert,
  Paper,
  Tabs,
  Tab,
  Badge,
} from '@mui/material';
import {
  Facebook as FacebookIcon,
  Twitter as TwitterIcon,
  Language as WebIcon,
  OpenInNew as OpenInNewIcon,
  YouTube as YouTubeIcon,
  Instagram as InstagramIcon,
} from '@mui/icons-material';
import { SocialSearchResult } from '../types/events';

interface SocialResultsPanelProps {
  results: SocialSearchResult[];
  query: string;
  sites: string[];
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`social-tabpanel-${index}`}
      aria-labelledby={`social-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const SocialResultsPanel: React.FC<SocialResultsPanelProps> = ({ results, query }) => {
  const [activeTab, setActiveTab] = useState(0);

  if (!results || results.length === 0) {
    return null;
  }

  // Separate results by platform
  const facebookResults = results.filter(r => 
    r.source_site.includes('facebook') || r.display_link.includes('facebook')
  );
  const twitterResults = results.filter(r => 
    r.source_site.includes('twitter') || r.source_site.includes('x.com') || 
    r.display_link.includes('twitter') || r.display_link.includes('x.com')
  );
  const youtubeResults = results.filter(r => 
    r.source_site.includes('youtube') || r.display_link.includes('youtube')
  );
  const instagramResults = results.filter(r => 
    r.source_site.includes('instagram') || r.display_link.includes('instagram')
  );
  const otherResults = results.filter(r => 
    !r.source_site.includes('facebook') && 
    !r.source_site.includes('twitter') && 
    !r.source_site.includes('x.com') &&
    !r.source_site.includes('youtube') &&
    !r.source_site.includes('instagram') &&
    !r.display_link.includes('facebook') && 
    !r.display_link.includes('twitter') &&
    !r.display_link.includes('x.com') &&
    !r.display_link.includes('youtube') &&
    !r.display_link.includes('instagram')
  );

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Get icon for site
  const getSiteIcon = (site: string) => {
    if (site.includes('facebook')) {
      return <FacebookIcon sx={{ fontSize: 20 }} />;
    } else if (site.includes('twitter') || site.includes('x.com')) {
      return <TwitterIcon sx={{ fontSize: 20 }} />;
    } else if (site.includes('youtube')) {
      return <YouTubeIcon sx={{ fontSize: 20 }} />;
    } else if (site.includes('instagram')) {
      return <InstagramIcon sx={{ fontSize: 20 }} />;
    }
    return <WebIcon sx={{ fontSize: 20 }} />;
  };

  // Get color for site chip
  const getSiteColor = (site: string): "primary" | "info" | "error" | "warning" | "default" => {
    if (site.includes('facebook')) return 'primary';
    if (site.includes('twitter') || site.includes('x.com')) return 'info';
    if (site.includes('youtube')) return 'error';
    if (site.includes('instagram')) return 'warning';
    return 'default';
  };

  // Extract image from pagemap
  const getImageFromResult = (result: SocialSearchResult): string | null => {
    console.log('Processing result from:', result.source_site, '| Title:', result.title);
    
    if (!result.pagemap) {
      console.log('❌ No pagemap found for:', result.source_site);
      return null;
    }
    
    const pagemap = result.pagemap;
    
    // Debug: Log pagemap structure for ALL results to compare
    console.log(`📋 Pagemap keys for ${result.source_site}:`, Object.keys(pagemap));
    
    // Extra debug for Facebook
    if (result.source_site.includes('facebook')) {
      console.log('🔍 === FACEBOOK RESULT DETAILED ===');
      console.log('Title:', result.title);
      console.log('Link:', result.link);
      console.log('Pagemap:', pagemap);
      console.log('Pagemap JSON:', JSON.stringify(pagemap, null, 2));
    }
    
    // Helper function to safely get image URL from various structures
    const tryGetImageUrl = (data: unknown): string | null => {
      if (!data) return null;
      
      // If it's a string, return it
      if (typeof data === 'string') return data;
      
      // If it's an array
      if (Array.isArray(data)) {
        if (data.length === 0) return null;
        const first = data[0];
        
        // Array of objects with src property
        if (typeof first === 'object' && first !== null && 'src' in first) {
          return first.src as string;
        }
        // Array of strings
        if (typeof first === 'string') {
          return first;
        }
        // Try recursively
        return tryGetImageUrl(first);
      }
      
      // If it's an object with src
      if (typeof data === 'object' && data !== null && 'src' in data) {
        return (data as { src: string }).src;
      }
      
      // If it's an object with url
      if (typeof data === 'object' && data !== null && 'url' in data) {
        return (data as { url: string }).url;
      }
      
      return null;
    };
    
    // 1. Check cse_image (most common)
    if (pagemap['cse_image']) {
      console.log('✓ Found cse_image field:', pagemap['cse_image']);
      const imageUrl = tryGetImageUrl(pagemap['cse_image']);
      if (imageUrl) {
        console.log('✅ Using cse_image:', imageUrl);
        return imageUrl;
      }
    }
    
    // 2. Check cse_thumbnail
    if (pagemap['cse_thumbnail']) {
      console.log('✓ Found cse_thumbnail field:', pagemap['cse_thumbnail']);
      const imageUrl = tryGetImageUrl(pagemap['cse_thumbnail']);
      if (imageUrl) {
        console.log('✅ Using cse_thumbnail:', imageUrl);
        return imageUrl;
      }
    }
    
    // 3. Check metatags (Facebook priority)
    if (pagemap['metatags']) {
      console.log('✓ Found metatags field:', pagemap['metatags']);
      const metatags = pagemap['metatags'];
      
      if (Array.isArray(metatags) && metatags.length > 0) {
        const meta = metatags[0] as Record<string, unknown>;
        console.log('  Metatags keys:', Object.keys(meta));
        
        // Try og:image (Open Graph)
        if (meta['og:image']) {
          const imageUrl = tryGetImageUrl(meta['og:image']);
          if (imageUrl) {
            console.log('✅ Using og:image:', imageUrl);
            return imageUrl;
          }
        }
        
        // Try twitter:image
        if (meta['twitter:image']) {
          const imageUrl = tryGetImageUrl(meta['twitter:image']);
          if (imageUrl) {
            console.log('✅ Using twitter:image:', imageUrl);
            return imageUrl;
          }
        }
        
        // Try twitter:image:src
        if (meta['twitter:image:src']) {
          const imageUrl = tryGetImageUrl(meta['twitter:image:src']);
          if (imageUrl) {
            console.log('✅ Using twitter:image:src:', imageUrl);
            return imageUrl;
          }
        }
      }
    }
    
    // 4. Check imageobject (structured data)
    if (pagemap['imageobject']) {
      console.log('✓ Found imageobject field:', pagemap['imageobject']);
      const imageUrl = tryGetImageUrl(pagemap['imageobject']);
      if (imageUrl) {
        console.log('✅ Using imageobject:', imageUrl);
        return imageUrl;
      }
    }
    
    // 5. Check webpage images
    if (pagemap['webpage']) {
      console.log('✓ Found webpage field:', pagemap['webpage']);
      const webpage = pagemap['webpage'];
      if (Array.isArray(webpage) && webpage.length > 0) {
        const page = webpage[0] as Record<string, unknown>;
        if (page['image']) {
          const imageUrl = tryGetImageUrl(page['image']);
          if (imageUrl) {
            console.log('✅ Using webpage image:', imageUrl);
            return imageUrl;
          }
        }
      }
    }
    
    console.log('❌ No image found in pagemap for:', result.source_site);
    return null;
  };

  // Proxy image URL for platforms that block CORS
  const getProxiedImageUrl = (imageUrl: string, sourceSite: string): string => {
    // Facebook and Instagram CDN often block CORS, so proxy them
    const needsProxy = sourceSite.includes('facebook') || 
                      sourceSite.includes('instagram') ||
                      imageUrl.includes('fbcdn.net') ||
                      imageUrl.includes('cdninstagram.com');
    
    if (needsProxy) {
      console.log('🔄 Using proxy for:', imageUrl);
      return `/api/v1/proxy-image?url=${encodeURIComponent(imageUrl)}`;
    }
    
    return imageUrl;
  };

  // Render result card - Google-style layout with image on left
  const renderResultCard = (result: SocialSearchResult, index: number, totalInTab: number) => {
    const imageUrl = getImageFromResult(result);
    const proxiedImageUrl = imageUrl ? getProxiedImageUrl(imageUrl, result.source_site) : null;
    
    return (
      <Card 
        key={index} 
        variant="outlined" 
        sx={{ 
          transition: 'all 0.2s',
          '&:hover': { 
            boxShadow: 3,
            transform: 'translateY(-2px)',
          }
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2 }}>
            {/* Left side - Image (if available) */}
            {proxiedImageUrl && (
              <Box
                sx={{
                  flexShrink: 0,
                  width: 120,
                  height: 120,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  overflow: 'hidden',
                  borderRadius: 1,
                  border: 1,
                  borderColor: 'divider',
                  bgcolor: 'grey.100',
                }}
              >
                <Box
                  component="img"
                  src={proxiedImageUrl}
                  alt={result.title}
                  sx={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                  }}
                  onError={(e: React.SyntheticEvent<HTMLImageElement>) => {
                    // Hide the entire image container if image fails to load
                    const parent = e.currentTarget.parentElement;
                    if (parent) parent.style.display = 'none';
                  }}
                />
              </Box>
            )}

            {/* Right side - Content */}
            <Box sx={{ flex: 1, minWidth: 0 }}>
              {/* Site Badge and Result Number */}
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Chip
                  icon={getSiteIcon(result.source_site)}
                  label={result.display_link}
                  color={getSiteColor(result.source_site)}
                  size="small"
                  variant="outlined"
                />
                <Typography variant="caption" color="text.secondary">
                  Result #{index + 1} of {totalInTab}
                </Typography>
              </Box>

              {/* Title */}
              <Link
                href={result.link}
                target="_blank"
                rel="noopener noreferrer"
                underline="hover"
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 0.5,
                  mb: 0.5,
                  color: 'primary.main',
                  fontWeight: 600,
                  fontSize: '1.1rem',
                  lineHeight: 1.3,
                  '&:hover': {
                    color: 'primary.dark',
                  }
                }}
              >
                <span style={{ flex: 1 }}>{result.title}</span>
                <OpenInNewIcon sx={{ fontSize: 16, flexShrink: 0, mt: 0.2 }} />
              </Link>

              {/* URL */}
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'success.main',
                  display: 'block',
                  wordBreak: 'break-all',
                  mb: 0.5,
                }}
              >
                {result.formatted_url}
              </Typography>

              {/* Snippet */}
              <Typography 
                variant="body2" 
                color="text.secondary" 
                sx={{ 
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  lineHeight: 1.5,
                }}
              >
                {result.snippet}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ width: '100%', mt: 3, mb: 3 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            🔍 Social Media Search Results
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Found <strong>{results.length}</strong> results for "<strong>{query}</strong>"
            {' '}({facebookResults.length} Facebook, {twitterResults.length} Twitter/X, 
            {youtubeResults.length} YouTube, {instagramResults.length} Instagram
            {otherResults.length > 0 && `, ${otherResults.length} Other`})
          </Typography>
          <Alert severity="info" sx={{ mt: 2 }}>
            These results are from social media platforms. Click on any link to view the original post.
          </Alert>
        </Box>

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange} 
            aria-label="social media tabs"
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab 
              icon={<Badge badgeContent={facebookResults.length} color="primary"><FacebookIcon /></Badge>}
              label="Facebook" 
              id="social-tab-0"
              aria-controls="social-tabpanel-0"
              sx={{ fontWeight: 600 }}
            />
            <Tab 
              icon={<Badge badgeContent={twitterResults.length} color="info"><TwitterIcon /></Badge>}
              label="Twitter / X" 
              id="social-tab-1"
              aria-controls="social-tabpanel-1"
              sx={{ fontWeight: 600 }}
            />
            <Tab 
              icon={<Badge badgeContent={youtubeResults.length} color="error"><YouTubeIcon /></Badge>}
              label="YouTube" 
              id="social-tab-2"
              aria-controls="social-tabpanel-2"
              sx={{ fontWeight: 600 }}
            />
            <Tab 
              icon={<Badge badgeContent={instagramResults.length} color="warning"><InstagramIcon /></Badge>}
              label="Instagram" 
              id="social-tab-3"
              aria-controls="social-tabpanel-3"
              sx={{ fontWeight: 600 }}
            />
            {otherResults.length > 0 && (
              <Tab 
                icon={<Badge badgeContent={otherResults.length} color="default"><WebIcon /></Badge>}
                label="Other" 
                id="social-tab-4"
                aria-controls="social-tabpanel-4"
                sx={{ fontWeight: 600 }}
              />
            )}
          </Tabs>
        </Box>

        {/* Facebook Tab */}
        <TabPanel value={activeTab} index={0}>
          {facebookResults.length > 0 ? (
            <Stack spacing={2}>
              {facebookResults.map((result, index) => 
                renderResultCard(result, index, facebookResults.length)
              )}
            </Stack>
          ) : (
            <Alert severity="info">
              No Facebook results found for this query.
            </Alert>
          )}
        </TabPanel>

        {/* Twitter Tab */}
        <TabPanel value={activeTab} index={1}>
          {twitterResults.length > 0 ? (
            <Stack spacing={2}>
              {twitterResults.map((result, index) => 
                renderResultCard(result, index, twitterResults.length)
              )}
            </Stack>
          ) : (
            <Alert severity="info">
              No Twitter/X results found for this query.
            </Alert>
          )}
        </TabPanel>

        {/* YouTube Tab */}
        <TabPanel value={activeTab} index={2}>
          {youtubeResults.length > 0 ? (
            <Stack spacing={2}>
              {youtubeResults.map((result, index) => 
                renderResultCard(result, index, youtubeResults.length)
              )}
            </Stack>
          ) : (
            <Alert severity="info">
              No YouTube results found for this query.
            </Alert>
          )}
        </TabPanel>

        {/* Instagram Tab */}
        <TabPanel value={activeTab} index={3}>
          {instagramResults.length > 0 ? (
            <Stack spacing={2}>
              {instagramResults.map((result, index) => 
                renderResultCard(result, index, instagramResults.length)
              )}
            </Stack>
          ) : (
            <Alert severity="info">
              No Instagram results found for this query.
            </Alert>
          )}
        </TabPanel>

        {/* Other Tab (if any) */}
        {otherResults.length > 0 && (
          <TabPanel value={activeTab} index={4}>
            <Stack spacing={2}>
              {otherResults.map((result, index) => 
                renderResultCard(result, index, otherResults.length)
              )}
            </Stack>
          </TabPanel>
        )}

        {/* Footer */}
        <Box sx={{ mt: 3, pt: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary" align="center" display="block">
            💡 Tip: Switch tabs to see results from different platforms. Click any link to view the full content.
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default SocialResultsPanel;
