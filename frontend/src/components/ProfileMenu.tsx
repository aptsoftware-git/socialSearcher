import React, { useState } from 'react';
import {
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  InputAdornment,
} from '@mui/material';
import { Visibility, VisibilityOff, CloudUpload } from '@mui/icons-material';

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

interface ProfileMenuProps {
  user: User;
  onUserUpdate: (updatedUser: User) => void;
}

const ProfileMenu: React.FC<ProfileMenuProps> = ({ user, onUserUpdate }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [profileDialogOpen, setProfileDialogOpen] = useState(false);
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  
  // Profile form state
  const [profileForm, setProfileForm] = useState({
    full_name: user.full_name || '',
    company: user.company || '',
    profile_image_url: user.profile_image_url || '',
  });
  
  // Password form state
  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });
  
  // Show/hide password state
  const [showOldPassword, setShowOldPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  // Image upload state
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(user.profile_image_url || null);
  
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Get display name based on priority: company > full_name > username
  const getDisplayName = () => {
    if (user.company) return user.company;
    if (user.full_name) return user.full_name;
    return user.username;
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleEditProfile = () => {
    setProfileDialogOpen(true);
    handleMenuClose();
    setError(null);
    setSuccess(null);
  };

  const handleChangePassword = () => {
    setPasswordDialogOpen(true);
    handleMenuClose();
    setError(null);
    setSuccess(null);
  };

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file');
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Image size should be less than 5MB');
        return;
      }
      
      setImageFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleProfileSubmit = async () => {
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      let profile_image_url = profileForm.profile_image_url;
      
      // If user uploaded an image, convert to base64
      if (imageFile) {
        const reader = new FileReader();
        profile_image_url = await new Promise<string>((resolve, reject) => {
          reader.onloadend = () => resolve(reader.result as string);
          reader.onerror = reject;
          reader.readAsDataURL(imageFile);
        });
      }
      
      const response = await fetch('/api/v1/auth/me', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          full_name: profileForm.full_name || null,
          company: profileForm.company || null,
          profile_image_url: profile_image_url || null,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update profile');
      }

      const updatedUser = await response.json();
      onUserUpdate(updatedUser);
      
      // Update localStorage
      localStorage.setItem('user', JSON.stringify(updatedUser));
      
      setSuccess('Profile updated successfully!');
      setTimeout(() => {
        setProfileDialogOpen(false);
        setSuccess(null);
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async () => {
    setError(null);
    setSuccess(null);

    // Validation
    if (!passwordForm.old_password || !passwordForm.new_password) {
      setError('Please fill in all fields');
      return;
    }

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setError('New passwords do not match');
      return;
    }

    if (passwordForm.new_password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/v1/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          old_password: passwordForm.old_password,
          new_password: passwordForm.new_password,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to change password');
      }

      setSuccess('Password changed successfully! Logging out...');
      setPasswordForm({ old_password: '', new_password: '', confirm_password: '' });
      
      // Auto-logout after password change
      setTimeout(() => {
        setPasswordDialogOpen(false);
        setSuccess(null);
        
        // Clear authentication data
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        
        // Redirect to login page or reload
        window.location.href = '/';
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <IconButton onClick={handleMenuOpen} sx={{ ml: 1 }}>
        <Avatar 
          src={user.profile_image_url} 
          alt={getDisplayName()}
          sx={{ width: 32, height: 32 }}
        >
          {getDisplayName().charAt(0).toUpperCase()}
        </Avatar>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={handleEditProfile}>Edit Profile</MenuItem>
        <MenuItem onClick={handleChangePassword}>Change Password</MenuItem>
      </Menu>

      {/* Edit Profile Dialog */}
      <Dialog open={profileDialogOpen} onClose={() => setProfileDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Profile</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            {error && <Alert severity="error">{error}</Alert>}
            {success && <Alert severity="success">{success}</Alert>}
            
            <TextField
              label="Full Name"
              value={profileForm.full_name}
              onChange={(e) => setProfileForm({ ...profileForm, full_name: e.target.value })}
              fullWidth
            />
            
            <TextField
              label="Company"
              value={profileForm.company}
              onChange={(e) => setProfileForm({ ...profileForm, company: e.target.value })}
              fullWidth
            />
            
            {/* Image Upload Section */}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Profile Image
              </Typography>
              
              {/* Image Preview */}
              {imagePreview && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <Avatar 
                    src={imagePreview} 
                    alt="Profile Preview"
                    sx={{ width: 120, height: 120 }}
                  />
                </Box>
              )}
              
              {/* Upload Button */}
              <Button
                component="label"
                variant="outlined"
                startIcon={<CloudUpload />}
                fullWidth
              >
                Upload Profile Image
                <input
                  type="file"
                  hidden
                  accept="image/*"
                  onChange={handleImageChange}
                />
              </Button>
              
              <Typography variant="caption" color="text.secondary">
                Recommended: Square image, max 5MB (JPG, PNG, GIF)
              </Typography>
            </Box>
            
            <Typography variant="caption" color="text.secondary">
              Email: {user.email}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Username: {user.username}
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProfileDialogOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleProfileSubmit} variant="contained" disabled={loading}>
            {loading ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Change Password Dialog */}
      <Dialog open={passwordDialogOpen} onClose={() => setPasswordDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            {error && <Alert severity="error">{error}</Alert>}
            {success && <Alert severity="success">{success}</Alert>}
            
            <TextField
              label="Current Password"
              type={showOldPassword ? 'text' : 'password'}
              value={passwordForm.old_password}
              onChange={(e) => setPasswordForm({ ...passwordForm, old_password: e.target.value })}
              fullWidth
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowOldPassword(!showOldPassword)}
                      edge="end"
                    >
                      {showOldPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            
            <TextField
              label="New Password"
              type={showNewPassword ? 'text' : 'password'}
              value={passwordForm.new_password}
              onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
              fullWidth
              helperText="Minimum 8 characters"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      edge="end"
                    >
                      {showNewPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            
            <TextField
              label="Confirm New Password"
              type={showConfirmPassword ? 'text' : 'password'}
              value={passwordForm.confirm_password}
              onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
              fullWidth
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      edge="end"
                    >
                      {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPasswordDialogOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handlePasswordSubmit} variant="contained" disabled={loading}>
            {loading ? 'Changing...' : 'Change Password'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ProfileMenu;
