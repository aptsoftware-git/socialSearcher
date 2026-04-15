import { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  Checkbox,
  FormControlLabel,
  CircularProgress,
  IconButton,
  InputAdornment,
  AppBar,
  Toolbar,
} from '@mui/material';
import { 
  Lock as LockIcon,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import logoImage from '../assets/aptvigilosint.webp';
import makeInIndiaLogo from '../assets/Make_In_India.png';

interface LoginProps {
  onLoginSuccess: (user: any, token: string) => void;
}

const Login = ({ onLoginSuccess }: LoginProps) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          remember_me: rememberMe,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Store token and user info
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Call success callback
      onLoginSuccess(data.user, data.access_token);
    } catch (err: any) {
      setError(err.message || 'Failed to login. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* App Bar / Header */}
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
        </Toolbar>
      </AppBar>

      {/* Main Content - Login Form */}
      <Container maxWidth="sm" sx={{ flex: 1, display: 'flex', alignItems: 'center', py: 3 }}>
        <Box
          sx={{
            width: '100%',
          }}
        >
          <Paper
            elevation={3}
            sx={{
              p: 3,
              width: '100%',
              maxWidth: 400,
            }}
          >
            {/* Logo */}
            <Box sx={{ textAlign: 'center', mb: 2 }}>
              <img
                src={logoImage}
                alt="Defender OSINT"
                style={{ width: '35%', marginBottom: '12px' }}
              />
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                <LockIcon color="primary" fontSize="small" />
                <Typography variant="h5" component="h1">
                  Sign In
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Enter your credentials to access the system
              </Typography>
            </Box>

            {/* Error Alert */}
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {/* Login Form */}
            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                margin="normal"
                required
                autoComplete="email"
                autoFocus
                disabled={loading}
              />

              <TextField
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                margin="normal"
                required
                autoComplete="current-password"
                disabled={loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle password visibility"
                        onClick={() => setShowPassword(!showPassword)}
                        onMouseDown={(e) => e.preventDefault()}
                        edge="end"
                        disabled={loading}
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <FormControlLabel
                control={
                  <Checkbox
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    disabled={loading}
                  />
                }
                label="Remember me"
                sx={{ mt: 1 }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading}
                sx={{ mt: 2, mb: 1.5 }}
              >
                {loading ? (
                  <>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>

            {/* Footer */}
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 1.5 }}>
              Contact your administrator if you don't have access
            </Typography>
          </Paper>
        </Box>
      </Container>

      {/* Footer */}
      <Box component="footer" sx={{ py: 1.5, px: 1.5, mt: 'auto', backgroundColor: (theme) => theme.palette.grey[200] }}>
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
  );
};

export default Login;
