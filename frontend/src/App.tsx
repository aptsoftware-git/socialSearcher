import { useState, useEffect } from 'react';
import { Container, CssBaseline, ThemeProvider, createTheme, AppBar, Toolbar, Typography, Box } from '@mui/material';
import SearchForm from './components/SearchForm';
import EventList from './components/EventList';
import ProgressBar from './components/ProgressBar';
import LLMConfigDropdown from './components/LLMConfigDropdown';
import SocialResultsPanel from './components/SocialResultsPanel';
import Login from './components/Login';
import AdminDashboard from './components/AdminDashboard';
import { EventData, ProgressUpdate, SocialSearchResult } from './types/events';
import { streamService } from './services/streamService';
import logoImage from './assets/defenderosint.webp';
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

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
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
  };

  const handleSocialSearchResults = (results: SocialSearchResult[], query: string, sites: string[]) => {
    setSocialResults(results);
    setSocialSearchQuery(query);
    setSocialSearchSites(sites);
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
              <Box component="span" sx={{ fontWeight: 'bold' }}>Tiger OSINT</Box> - AI based customized web scrapper
            </Typography>
            <Typography variant="body2" sx={{ mr: 2 }}>
              {user?.email}
            </Typography>
            <LLMConfigDropdown />
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