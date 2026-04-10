import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Popover,
  Divider,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  DataUsage as DataUsageIcon,
} from '@mui/icons-material';
import Badge from '@mui/material/Badge';

interface QuotaDailyBreakdown {
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
}

interface QuotaStatus {
  has_limit: boolean;
  search_limit: number | null;
  quota_start_date: string | null;
  quota_end_date: string | null;
  searches_used: number;
  total_scrapings: number;
  total_analyses: number;
  percentage: number;
  period_label: string;
  period_expired: boolean;
  daily_breakdown: QuotaDailyBreakdown[];
}

interface SearchQuotaBarProps {
  token: string;
  /** Called when quota status changes so the parent can block searching if exceeded */
  onQuotaExceeded?: (exceeded: boolean) => void;
}

const SearchQuotaBar = ({ token, onQuotaExceeded }: SearchQuotaBarProps) => {
  const [quota, setQuota] = useState<QuotaStatus | null>(null);
  const [popoverAnchor, setPopoverAnchor] = useState<HTMLElement | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const fetchQuota = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/auth/my-quota', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) return;
      const data: QuotaStatus = await response.json();
      setQuota(data);
      if (onQuotaExceeded) {
        onQuotaExceeded(
          data.has_limit &&
            data.search_limit !== null &&
            (data.searches_used >= data.search_limit || data.period_expired)
        );
      }
    } catch {
      // silently ignore quota fetch errors
    }
  }, [token, onQuotaExceeded]);

  useEffect(() => {
    fetchQuota();
  }, [fetchQuota]);

  // Don't render if no limit is set
  if (!quota || !quota.has_limit || quota.search_limit === null) return null;

  const exceeded = quota.searches_used >= quota.search_limit || quota.period_expired;
  const nearLimit = quota.percentage >= 80 && !exceeded;

  const barColor = exceeded ? 'error' : nearLimit ? 'warning' : 'primary';

  const formatDate = (ds: string | null) =>
    ds ? new Date(ds).toLocaleDateString() : '—';

  const totalRow: Partial<QuotaDailyBreakdown> = quota.daily_breakdown.reduce(
    (acc, d) => ({
      total_searches: (acc.total_searches ?? 0) + d.total_searches,
      youtube_searches: (acc.youtube_searches ?? 0) + d.youtube_searches,
      twitter_searches: (acc.twitter_searches ?? 0) + d.twitter_searches,
      facebook_searches: (acc.facebook_searches ?? 0) + d.facebook_searches,
      instagram_searches: (acc.instagram_searches ?? 0) + d.instagram_searches,
      google_searches: (acc.google_searches ?? 0) + d.google_searches,
      total_scrapings: (acc.total_scrapings ?? 0) + d.total_scrapings,
      paid_scrapings: (acc.paid_scrapings ?? 0) + d.paid_scrapings,
      free_scrapings: (acc.free_scrapings ?? 0) + d.free_scrapings,
      total_analyses: (acc.total_analyses ?? 0) + d.total_analyses,
    }),
    {} as Partial<QuotaDailyBreakdown>
  );

  const openPopover = (e: React.MouseEvent<HTMLElement>) => {
    setPopoverAnchor(e.currentTarget);
    fetchQuota();
  };

  return (
    <>
      {/* Toolbar icon */}
      <Tooltip title="Search Usage">
        <IconButton
          size="small"
          onClick={openPopover}
          sx={{
            color: exceeded ? '#ffcdd2' : nearLimit ? '#ffe0b2' : 'rgba(255,255,255,0.9)',
            mx: 0.5,
          }}
        >
          <Badge
            variant="dot"
            color={exceeded ? 'error' : 'warning'}
            invisible={!exceeded && !nearLimit}
          >
            <DataUsageIcon fontSize="small" />
          </Badge>
        </IconButton>
      </Tooltip>

      {/* Popover — progress bar + summary */}
      <Popover
        open={Boolean(popoverAnchor)}
        anchorEl={popoverAnchor}
        onClose={() => setPopoverAnchor(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        PaperProps={{ sx: { p: 2.5, minWidth: 320, maxWidth: 380 } }}
      >
        {/* Header */}
        <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 0.5 }}>Search Usage</Typography>

        <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1.5 }}>
          {quota.period_label || `${formatDate(quota.quota_start_date)} – ${formatDate(quota.quota_end_date)}`}
        </Typography>

        {/* Progress bar */}
        <LinearProgress
          variant="determinate"
          value={Math.min(100, quota.percentage)}
          color={barColor}
          sx={{ height: 10, borderRadius: 5, mb: 1, backgroundColor: 'rgba(0,0,0,0.08)' }}
        />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="body2" color={exceeded ? 'error.main' : 'text.secondary'}>
            {quota.searches_used} / {quota.search_limit} searches
          </Typography>
          <Typography variant="body2" fontWeight="bold" color={exceeded ? 'error.main' : nearLimit ? 'warning.main' : 'success.main'}>
            {quota.percentage}%
          </Typography>
        </Box>

        {/* Exceeded warning */}
        {exceeded && (
          <Box sx={{ mb: 2, p: 1.5, backgroundColor: '#ffcdd2', borderRadius: 1, border: 1, borderColor: '#e57373' }}>
            <Typography variant="caption" color="error.dark" fontWeight="medium">
              {quota.period_expired
                ? `Quota period expired (${quota.period_label}). Contact admin to renew.`
                : 'Search quota exhausted. Contact admin to increase your limit.'}
            </Typography>
          </Box>
        )}

        <Divider sx={{ mb: 1.5 }} />

        {/* Details button */}
        <Button
          fullWidth
          variant="outlined"
          size="small"
          onClick={() => { setPopoverAnchor(null); setDetailsOpen(true); }}
        >
          Details
        </Button>
      </Popover>

      {/* Dialog — full daily breakdown table */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Search Quota Details</DialogTitle>
        <DialogContent dividers>
          {/* Summary */}
          <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Quota Period
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {quota.period_label || `${formatDate(quota.quota_start_date)} – ${formatDate(quota.quota_end_date)}`}
            </Typography>

            <Stack direction="row" spacing={3} flexWrap="wrap" sx={{ mb: 2 }}>
              <Box>
                <Typography variant="caption" color="text.secondary">Searches Used</Typography>
                <Typography variant="h5" fontWeight="bold" color={exceeded ? 'error.main' : nearLimit ? 'warning.main' : 'text.primary'}>
                  {quota.searches_used}
                  <Box component="span" sx={{ fontSize: '0.6em', fontWeight: 'normal', color: 'text.secondary', ml: 0.5 }}>/ {quota.search_limit}</Box>
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Total Scrapings</Typography>
                <Typography variant="h5" fontWeight="bold">{quota.total_scrapings}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Total Analyses</Typography>
                <Typography variant="h5" fontWeight="bold">{quota.total_analyses}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Usage</Typography>
                <Typography variant="h5" fontWeight="bold" color={exceeded ? 'error.main' : nearLimit ? 'warning.main' : 'success.main'}>
                  {quota.percentage}%
                </Typography>
              </Box>
            </Stack>

            <LinearProgress
              variant="determinate"
              value={Math.min(100, quota.percentage)}
              color={barColor}
              sx={{ height: 8, borderRadius: 4, mb: 1, backgroundColor: 'rgba(0,0,0,0.08)' }}
            />
            <Typography variant="caption" color="text.secondary">{quota.percentage}% used</Typography>

            {exceeded && (
              <Box sx={{ mt: 2, p: 1.5, backgroundColor: '#ffcdd2', borderRadius: 1, border: 1, borderColor: '#e57373' }}>
                <Typography variant="body2" color="error.dark" fontWeight="medium">
                  {quota.period_expired
                    ? `Your quota period has expired (${quota.period_label}). Please contact your administrator to renew your quota period.`
                    : 'Your search quota has been exhausted. Please contact your administrator to increase your limit or extend your quota period.'}
                </Typography>
              </Box>
            )}
          </Paper>

          {/* Daily breakdown */}
          {quota.daily_breakdown.length > 0 ? (
            <>
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                Daily Breakdown
              </Typography>
              <TableContainer component={Paper} variant="outlined">
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
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {quota.daily_breakdown.map((day) => (
                      <TableRow key={day.usage_date}>
                        <TableCell>
                          {new Date(day.usage_date).toLocaleDateString()}
                        </TableCell>
                        <TableCell align="right">{day.youtube_searches}</TableCell>
                        <TableCell align="right">{day.twitter_searches}</TableCell>
                        <TableCell align="right">{day.facebook_searches}</TableCell>
                        <TableCell align="right">{day.instagram_searches}</TableCell>
                        <TableCell align="right">{day.google_searches}</TableCell>
                        <TableCell align="right">{day.paid_scrapings}</TableCell>
                        <TableCell align="right">{day.free_scrapings}</TableCell>
                        <TableCell align="right">{day.total_analyses}</TableCell>
                      </TableRow>
                    ))}
                    {/* Total row */}
                    <TableRow sx={{ backgroundColor: 'action.hover', fontWeight: 'bold' }}>
                      <TableCell sx={{ fontWeight: 'bold' }}>TOTAL</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>{totalRow.youtube_searches ?? 0}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>{totalRow.twitter_searches ?? 0}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>{totalRow.facebook_searches ?? 0}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>{totalRow.instagram_searches ?? 0}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>{totalRow.google_searches ?? 0}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>{totalRow.paid_scrapings ?? 0}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>{totalRow.free_scrapings ?? 0}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>{totalRow.total_analyses ?? 0}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </>
          ) : (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
              No activity in quota period yet.
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)} variant="contained">Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default SearchQuotaBar;
