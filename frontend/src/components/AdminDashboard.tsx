import { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Checkbox,
  Alert,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  InputAdornment,
  Tooltip,
  Avatar,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Assessment as AssessmentIcon,
  People as PeopleIcon,
  Visibility,
  VisibilityOff,
  VpnKey as VpnKeyIcon,
} from '@mui/icons-material';

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
  search_limit?: number | null;
  quota_start_date?: string | null;
  quota_end_date?: string | null;
}

interface UsageReport {
  usage_date: string;
  total_searches: number;
  youtube_searches: number;
  twitter_searches: number;
  facebook_searches: number;
  instagram_searches: number;
  google_searches: number;
  total_scrapings: number;
  paid_scrapings: number;
  free_scrapings: number;
  total_analyses: number;
  google_api_calls: number;
  scrapecreators_credits: number;
  claude_tokens: number;
  daily_cost_usd: number;
}

interface MonthlySummary {
  year: number;
  month: number;
  total_searches: number;
  youtube_searches: number;
  twitter_searches: number;
  facebook_searches: number;
  instagram_searches: number;
  google_searches: number;
  total_scrapings: number;
  paid_scrapings: number;
  free_scrapings: number;
  total_analyses: number;
  google_api_calls: number;
  scrapecreators_credits: number;
  claude_tokens: number;
  monthly_cost_usd: number;
  daily_breakdown: UsageReport[];
}

interface AdminDashboardProps {
  token: string;
  onLogout: () => void;
}

const AdminDashboard = ({ token, onLogout }: AdminDashboardProps) => {
  const [tabValue, setTabValue] = useState(0);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // User management state
  const [openUserDialog, setOpenUserDialog] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [userForm, setUserForm] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
    company: '',
    is_admin: false,
    is_active: true,
    search_limit: '' as string | number,
    quota_start_date: '',
    quota_end_date: '',
  });

  // Usage report state
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [reportYear, setReportYear] = useState(new Date().getFullYear());
  const [reportMonth, setReportMonth] = useState(new Date().getMonth() + 1);
  const [usageReport, setUsageReport] = useState<MonthlySummary | null>(null);
  const [reportUser, setReportUser] = useState<User | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await fetch('/api/v1/users/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch users' }));
        throw new Error(errorData.detail || 'Failed to fetch users');
      }

      const data = await response.json();
      setUsers(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Error fetching users:', err);
      setError(err.message || 'Failed to fetch users. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Generate secure random password
  const generatePassword = () => {
    const length = 12;
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let password = '';
    
    // Ensure at least one of each required character type
    password += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[Math.floor(Math.random() * 26)]; // Uppercase
    password += 'abcdefghijklmnopqrstuvwxyz'[Math.floor(Math.random() * 26)]; // Lowercase
    password += '0123456789'[Math.floor(Math.random() * 10)]; // Digit
    password += '!@#$%^&*'[Math.floor(Math.random() * 8)]; // Special char
    
    // Fill the rest randomly
    for (let i = password.length; i < length; i++) {
      password += charset[Math.floor(Math.random() * charset.length)];
    }
    
    // Shuffle the password
    return password.split('').sort(() => Math.random() - 0.5).join('');
  };

  const handleCreateUser = () => {
    setEditingUser(null);
    const autoPassword = generatePassword();
    const today = new Date();
    const nextYear = new Date(today);
    nextYear.setFullYear(nextYear.getFullYear() + 1);
    setUserForm({
      email: '',
      username: '',
      password: autoPassword,
      full_name: '',
      company: '',
      is_admin: false,
      is_active: true,
      search_limit: '',
      quota_start_date: today.toISOString().split('T')[0],
      quota_end_date: nextYear.toISOString().split('T')[0],
    });
    setShowPassword(false);
    setOpenUserDialog(true);
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setUserForm({
      email: user.email,
      username: user.username,
      password: '', // Empty initially, only fill if resetting
      full_name: user.full_name || '',
      company: user.company || '',
      is_admin: user.is_admin,
      is_active: user.is_active,
      search_limit: user.search_limit != null ? user.search_limit : '',
      quota_start_date: user.quota_start_date || '',
      quota_end_date: user.quota_end_date || '',
    });
    setShowPassword(false);
    setOpenUserDialog(true);
  };

  const handleSaveUser = async () => {
    try {
      setLoading(true);
      setError('');

      if (editingUser) {
        // Update existing user
        const updateData: any = {
          email: userForm.email,
          username: userForm.username,
          full_name: userForm.full_name || null,
          company: userForm.company || null,
          is_active: userForm.is_active,
        };

        // Quota fields
        if (userForm.search_limit !== '' && userForm.search_limit !== null) {
          updateData.search_limit = Number(userForm.search_limit);
        } else {
          updateData.clear_search_limit = true;
        }
        if (userForm.quota_start_date) updateData.quota_start_date = userForm.quota_start_date;
        if (userForm.quota_end_date) updateData.quota_end_date = userForm.quota_end_date;
        
        // Debug: Show what we're sending
        console.log('Password field value:', userForm.password);
        console.log('Password length:', userForm.password ? userForm.password.length : 0);
        
        // Only include password if it's provided (for password reset)
        if (userForm.password && userForm.password.trim() !== '') {
          updateData.password = userForm.password;
          console.log('Password WILL be sent');
        } else {
          console.log('Password will NOT be sent (empty or whitespace)');
        }
        
        console.log('Update data:', updateData);
        
        const response = await fetch(`/api/v1/users/${editingUser.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(updateData),
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Failed to update user');
        }

        setSuccess('User updated successfully');
      } else {
        // Create new user
        const response = await fetch('/api/v1/users/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            ...userForm,
            search_limit: userForm.search_limit !== '' ? Number(userForm.search_limit) : undefined,
            quota_start_date: userForm.quota_start_date || undefined,
            quota_end_date: userForm.quota_end_date || undefined,
          }),
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Failed to create user');
        }

        setSuccess(`User created successfully. Temporary password: ${userForm.password}`);
      }

      setOpenUserDialog(false);
      fetchUsers();
    } catch (err: any) {
      setError(err.message || 'Failed to save user');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleUserStatus = async (user: User) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/users/${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          is_active: !user.is_active,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to toggle user status');
      }

      setSuccess(`User ${user.is_active ? 'deactivated' : 'activated'} successfully`);
      fetchUsers();
    } catch (err: any) {
      setError(err.message || 'Failed to toggle user status');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsageReport = async () => {
    if (!selectedUserId) {
      setError('Please select a user');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/api/v1/users/usage-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: selectedUserId,
          year: reportYear,
          month: reportMonth,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch usage report');
      }

      const data = await response.json();
      setUsageReport(data.usage);
      setReportUser(data.user);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch usage report');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return `$${amount.toFixed(4)}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">Admin Dashboard</Typography>
        <Button variant="outlined" onClick={onLogout}>
          Logout
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab icon={<PeopleIcon />} label="User Management" />
          <Tab icon={<AssessmentIcon />} label="Usage Reports" />
        </Tabs>
      </Paper>

      {/* User Management Tab */}
      {tabValue === 0 && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">Users</Typography>
            <Box>
              <IconButton onClick={fetchUsers} disabled={loading}>
                <RefreshIcon />
              </IconButton>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleCreateUser}
                disabled={loading}
              >
                Add User
              </Button>
            </Box>
          </Box>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Profile</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Username</TableCell>
                  <TableCell>Full Name</TableCell>
                  <TableCell>Company</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Last Login</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <Avatar
                        src={user.profile_image_url}
                        alt={user.full_name || user.username}
                        sx={{ width: 40, height: 40 }}
                      >
                        {!user.profile_image_url && (user.full_name?.[0] || user.username[0]).toUpperCase()}
                      </Avatar>
                    </TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{user.full_name || '-'}</TableCell>
                    <TableCell>{user.company || '-'}</TableCell>
                    <TableCell>
                      <Chip
                        label={user.is_admin ? 'Admin' : 'User'}
                        color={user.is_admin ? 'error' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={user.is_active ? 'Active' : 'Inactive'}
                        color={user.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {user.last_login ? formatDate(user.last_login) : 'Never'}
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleEditUser(user)}
                        disabled={loading}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleToggleUserStatus(user)}
                        disabled={loading}
                        color={user.is_active ? 'error' : 'success'}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {/* Usage Reports Tab */}
      {tabValue === 1 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ mb: 3 }}>
            User Usage Report
          </Typography>

          <Stack direction="column" spacing={2} sx={{ mb: 3 }}>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
              <Box sx={{ flex: 2 }}>
                <FormControl fullWidth>
                  <InputLabel>Select User</InputLabel>
                  <Select
                    value={selectedUserId || ''}
                    onChange={(e) => setSelectedUserId(Number(e.target.value))}
                    label="Select User"
                  >
                    {users.filter(u => !u.is_admin).map((user) => (
                      <MenuItem key={user.id} value={user.id}>
                        {user.email} ({user.username})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              <Box sx={{ flex: 1 }}>
                <TextField
                  fullWidth
                  label="Year"
                  type="number"
                  value={reportYear}
                  onChange={(e) => setReportYear(Number(e.target.value))}
                />
              </Box>

              <Box sx={{ flex: 1 }}>
                <FormControl fullWidth>
                  <InputLabel>Month</InputLabel>
                  <Select
                    value={reportMonth}
                    onChange={(e) => setReportMonth(Number(e.target.value))}
                    label="Month"
                  >
                    {Array.from({ length: 12 }, (_, i) => (
                      <MenuItem key={i + 1} value={i + 1}>
                        {new Date(2000, i).toLocaleString('default', { month: 'long' })}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              <Box sx={{ flex: 1 }}>
                <Button
                  fullWidth
                  variant="contained"
                  onClick={fetchUsageReport}
                  disabled={loading || !selectedUserId}
                  sx={{ height: '56px' }}
                >
                  Generate Report
                </Button>
              </Box>
            </Stack>
          </Stack>

          {usageReport && reportUser && (
            <Box>
              {/* Monthly Summary */}
              <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Monthly Summary for {reportUser.email}
                </Typography>
                <Stack direction="row" spacing={2} flexWrap="wrap">
                  <Box sx={{ minWidth: 120 }}>
                    <Typography variant="caption" color="text.secondary">
                      Total Searches
                    </Typography>
                    <Typography variant="h6">{usageReport.total_searches}</Typography>
                  </Box>
                  <Box sx={{ minWidth: 120 }}>
                    <Typography variant="caption" color="text.secondary">
                      Total Scrapings
                    </Typography>
                    <Typography variant="h6">{usageReport.total_scrapings}</Typography>
                  </Box>
                  <Box sx={{ minWidth: 120 }}>
                    <Typography variant="caption" color="text.secondary">
                      Total Analyses
                    </Typography>
                    <Typography variant="h6">{usageReport.total_analyses}</Typography>
                  </Box>
                  <Box sx={{ minWidth: 120 }}>
                    <Typography variant="caption" color="text.secondary">
                      Total Cost
                    </Typography>
                    <Typography variant="h6" color="primary">
                      {formatCurrency(usageReport.monthly_cost_usd)}
                    </Typography>
                  </Box>
                </Stack>
              </Paper>

              {/* Daily Breakdown */}
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Daily Breakdown
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell align="right">YouTube</TableCell>
                      <TableCell align="right">Twitter</TableCell>
                      <TableCell align="right">Facebook</TableCell>
                      <TableCell align="right">Instagram</TableCell>
                      <TableCell align="right">Google</TableCell>
                      <TableCell align="right">Paid Scrapings</TableCell>
                      <TableCell align="right">Free Scrapings</TableCell>
                      <TableCell align="right">Analyses</TableCell>
                      <TableCell align="right">Daily Cost</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {usageReport.daily_breakdown.map((day) => (
                      <TableRow key={day.usage_date}>
                        <TableCell>{formatDate(day.usage_date)}</TableCell>
                        <TableCell align="right">{day.youtube_searches}</TableCell>
                        <TableCell align="right">{day.twitter_searches}</TableCell>
                        <TableCell align="right">{day.facebook_searches}</TableCell>
                        <TableCell align="right">{day.instagram_searches}</TableCell>
                        <TableCell align="right">{day.google_searches}</TableCell>
                        <TableCell align="right">{day.paid_scrapings}</TableCell>
                        <TableCell align="right">{day.free_scrapings}</TableCell>
                        <TableCell align="right">{day.total_analyses}</TableCell>
                        <TableCell align="right">
                          {formatCurrency(day.daily_cost_usd)}
                        </TableCell>
                      </TableRow>
                    ))}
                    <TableRow sx={{ fontWeight: 'bold', backgroundColor: 'action.hover' }}>
                      <TableCell>TOTAL</TableCell>
                      <TableCell align="right">{usageReport.youtube_searches}</TableCell>
                      <TableCell align="right">{usageReport.twitter_searches}</TableCell>
                      <TableCell align="right">{usageReport.facebook_searches}</TableCell>
                      <TableCell align="right">{usageReport.instagram_searches}</TableCell>
                      <TableCell align="right">{usageReport.google_searches}</TableCell>
                      <TableCell align="right">{usageReport.paid_scrapings}</TableCell>
                      <TableCell align="right">{usageReport.free_scrapings}</TableCell>
                      <TableCell align="right">{usageReport.total_analyses}</TableCell>
                      <TableCell align="right">
                        {formatCurrency(usageReport.monthly_cost_usd)}
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Cost Calculation Note - Moved to bottom */}
              <Paper variant="outlined" sx={{ p: 2, mt: 3, backgroundColor: 'info.lighter' }}>
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom color="info.main">
                  💡 How Daily Cost is Calculated
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • <strong>Searches:</strong> $0.005 per platform searched (Google CSE API)
                  <br />
                  • <strong>Paid Scrapings:</strong> Cost only when fetching new content (not from cache):
                  <br />
                  &nbsp;&nbsp;- Twitter, Facebook, Instagram: $0.001 per fetch (api.scrapecreators.com)
                  <br />
                  &nbsp;&nbsp;- YouTube: $0.0005 per fetch (Google CSE API)
                  <br />
                  • <strong>Free Scrapings:</strong> Google search results: $0 (free internal scraping)
                  <br />
                  • <strong>Analyses:</strong> Cost only when calling LLM API (not from cache):
                  <br />
                  &nbsp;&nbsp;- Claude API: $0.001-$0.005 per analysis (varies by tokens used)
                  <br />
                  &nbsp;&nbsp;- Ollama (local): $0 (free)
                  <br />
                  <br />
                  <Typography variant="caption" sx={{ fontStyle: 'italic' }}>
                    Note: Cached content and cached analyses are served at zero cost. Only actual API calls are tracked.
                  </Typography>
                </Typography>
              </Paper>
            </Box>
          )}
        </Paper>
      )}

      {/* User Dialog */}
      <Dialog open={openUserDialog} onClose={() => setOpenUserDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingUser ? 'Edit User' : 'Create New User'}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={userForm.email}
              onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}
              margin="normal"
              required
              disabled={!!editingUser}
            />

            <TextField
              fullWidth
              label="Username"
              value={userForm.username}
              onChange={(e) => setUserForm({ ...userForm, username: e.target.value })}
              margin="normal"
              required
              disabled={!!editingUser}
            />

            <TextField
              fullWidth
              label={editingUser ? "New Password (leave empty to keep current)" : "Password"}
              type={showPassword ? 'text' : 'password'}
              value={userForm.password}
              onChange={(e) => setUserForm({ ...userForm, password: e.target.value })}
              margin="normal"
              required={!editingUser}
              helperText={
                editingUser 
                  ? "Enter new password to reset, or leave empty to keep current password"
                  : "Minimum 8 characters with uppercase, lowercase, number, and special character"
              }
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <Tooltip title="Generate new password">
                      <IconButton
                        onClick={() => setUserForm({ ...userForm, password: generatePassword() })}
                        edge="end"
                        size="small"
                      >
                        <VpnKeyIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={showPassword ? 'Hide password' : 'Show password'}>
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        onMouseDown={(e) => e.preventDefault()}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </Tooltip>
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Full Name"
              value={userForm.full_name}
              onChange={(e) => setUserForm({ ...userForm, full_name: e.target.value })}
              margin="normal"
            />

            <TextField
              fullWidth
              label="Company"
              value={userForm.company}
              onChange={(e) => setUserForm({ ...userForm, company: e.target.value })}
              margin="normal"
            />

            <Box sx={{ mt: 2, mb: 1 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Search Quota (optional)
              </Typography>
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <TextField
                  label="Search Limit"
                  type="number"
                  value={userForm.search_limit}
                  onChange={(e) => setUserForm({ ...userForm, search_limit: e.target.value })}
                  helperText="Leave empty for no limit"
                  inputProps={{ min: 0 }}
                  sx={{ flex: 1 }}
                />
                <TextField
                  label="Period Start"
                  type="date"
                  value={userForm.quota_start_date}
                  onChange={(e) => setUserForm({ ...userForm, quota_start_date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                  sx={{ flex: 1 }}
                />
                <TextField
                  label="Period End"
                  type="date"
                  value={userForm.quota_end_date}
                  onChange={(e) => setUserForm({ ...userForm, quota_end_date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                  sx={{ flex: 1 }}
                />
              </Stack>
            </Box>

            {!editingUser && (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={userForm.is_admin}
                    onChange={(e) => setUserForm({ ...userForm, is_admin: e.target.checked })}
                  />
                }
                label="Administrator privileges"
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenUserDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveUser} variant="contained" disabled={loading}>
            {editingUser ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AdminDashboard;
