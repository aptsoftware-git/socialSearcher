import React, { useState, useEffect } from 'react';
import {
  Box,
  IconButton,
  Menu,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Divider,
  Typography,
  Chip,
  Alert,
  SelectChangeEvent,
  Tooltip,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

interface LLMModel {
  id: string;
  name: string;
  description?: string;
  pricing?: {
    input: number;
    output: number;
    cache_discount?: number;
  };
}

interface LLMUsage {
  total_requests: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_cached_tokens: number;
  total_cost: number;
  cache_savings: number;
}

interface LLMConfig {
  provider: 'claude';  // Removed 'ollama' option
  model: string;
}

const STORAGE_KEY = 'llm_config';

const LLMConfigDropdown: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [config, setConfig] = useState<LLMConfig>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error('Failed to parse saved LLM config:', e);
      }
    }
    return { provider: 'claude', model: 'claude-sonnet-4-6' };
  });

  const [models, setModels] = useState<{ claude: LLMModel[] }>({
    claude: [],
  });
  const [usage, setUsage] = useState<LLMUsage | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const open = Boolean(anchorEl);

  // Fetch available models
  const fetchModels = async () => {
    try {
      const response = await fetch('/api/v1/llm/models');
      const data = await response.json();

      if (data.models) {
        const claudeModels = Array.isArray(data.models.claude?.models)
          ? data.models.claude.models
          : [];

        setModels({
          claude: claudeModels,
        });

        const defaultModel = data.models.claude?.default || 'claude-sonnet-4-6';

        setConfig(prev => {
          const modelExists = claudeModels.some((m: LLMModel) => m.id === prev.model);
          if (!modelExists) {
            return {
              ...prev,
              model: defaultModel,
            };
          }
          return prev;
        });
      }
    } catch (err) {
    }
  };

  // Fetch usage stats
  const fetchUsage = async () => {
    try {
      const response = await fetch('/api/v1/llm/usage');
      const data = await response.json();

      if (data.usage) {
        setUsage(data.usage);
      }
    } catch (err) {
      console.error('Failed to fetch usage:', err);
    }
  };

  // Reset usage stats
  const resetStats = async () => {
    try {
      setLoading(true);
      await fetch('/api/v1/llm/reset-stats', { method: 'POST' });
      await fetchUsage(); // Refresh
      setLoading(false);
    } catch (err) {
      console.error('Failed to reset stats:', err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
    fetchUsage();
    // Refresh usage every 30 seconds if menu is open
    const interval = open
      ? setInterval(fetchUsage, 30000)
      : undefined;
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [open]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  }, [config]);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
    setError(null);
  };

  const handleModelChange = (event: SelectChangeEvent<string>) => {
    setConfig((prev) => ({
      ...prev,
      model: event.target.value,
    }));
  };

  return (
    <>
      <Tooltip title="LLM Configuration">
        <IconButton
          color="inherit"
          onClick={handleClick}
          sx={{ ml: 1 }}
        >
          <SettingsIcon />
        </IconButton>
      </Tooltip>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        PaperProps={{
          sx: { minWidth: 320, maxWidth: 400 }
        }}
      >
        <Box sx={{ px: 2, py: 1.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
            <SettingsIcon fontSize="small" />
            <Typography variant="subtitle2" fontWeight="medium">
              LLM Configuration
            </Typography>
            <Chip
              label="Claude"
              size="small"
              color="primary"
            />
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Model Selection - Removed Provider Selection */}
          <FormControl fullWidth size="small">
            <InputLabel>Model</InputLabel>
            <Select
              value={config.model}
              label="Model"
              onChange={handleModelChange}
            >
              {models.claude.length > 0 
                ? models.claude.map((model) => (
                    <MenuItem key={model.id} value={model.id}>
                      {model.name}
                    </MenuItem>
                  ))
                : [
                    <MenuItem key="claude-sonnet-4-6" value="claude-sonnet-4-6">
                      Claude Sonnet 4.6 (Default)
                    </MenuItem>,
                    <MenuItem key="claude-opus-4-6" value="claude-opus-4-6">
                      Claude Opus 4.6 (Best Quality)
                    </MenuItem>
                  ]
              }
            </Select>
          </FormControl>

          {/* Model Pricing Info */}
          {models.claude.length > 0 && (
            <>
              <Divider sx={{ my: 1.5 }} />
              <Box>
                <Typography variant="caption" color="text.secondary" fontWeight="medium">
                  Pricing (per 1M tokens)
                </Typography>
                {models.claude
                  .filter((model) => model.id === config.model)
                  .map((model) => model.pricing ? (
                    <Box key={model.id} sx={{ mt: 0.5, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                      <Box>
                        <Typography variant="caption" color="text.secondary">Input</Typography>
                        <Typography variant="body2" fontSize="0.75rem">${model.pricing.input}</Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary">Output</Typography>
                        <Typography variant="body2" fontSize="0.75rem">${model.pricing.output}</Typography>
                      </Box>
                      {model.pricing.cache_discount !== undefined && (
                        <Box sx={{ gridColumn: '1 / -1' }}>
                          <Typography variant="caption" color="success.main">
                            Cache: {model.pricing.cache_discount}% discount
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  ) : null)}
              </Box>
            </>
          )}

          {/* Usage Stats for Claude */}
          {usage && (
            <>
              <Divider sx={{ my: 1.5 }} />
              <Box>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    mb: 1,
                  }}
                >
                  <Typography variant="caption" color="text.secondary" fontWeight="medium">
                    Usage Statistics
                  </Typography>
                  <IconButton size="small" onClick={resetStats} disabled={loading}>
                    <RefreshIcon fontSize="small" />
                  </IconButton>
                </Box>

                <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                  <Box>
                    <Typography variant="caption" color="text.secondary" fontSize="0.7rem">
                      Requests
                    </Typography>
                    <Typography variant="body2" fontSize="0.75rem">{usage.total_requests || 0}</Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" color="text.secondary" fontSize="0.7rem">
                      Total Cost
                    </Typography>
                    <Typography variant="body2" fontSize="0.75rem" fontWeight="medium" color="primary">
                      ${(usage.total_cost || 0).toFixed(4)}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" color="text.secondary" fontSize="0.7rem">
                      Input Tokens
                    </Typography>
                    <Typography variant="body2" fontSize="0.75rem">
                      {(usage.total_input_tokens || 0).toLocaleString()}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" color="text.secondary" fontSize="0.7rem">
                      Output Tokens
                    </Typography>
                    <Typography variant="body2" fontSize="0.75rem">
                      {(usage.total_output_tokens || 0).toLocaleString()}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" color="text.secondary" fontSize="0.7rem">
                      Cached Tokens
                    </Typography>
                    <Typography variant="body2" fontSize="0.75rem" color="success.main">
                      {(usage.total_cached_tokens || 0).toLocaleString()}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" color="text.secondary" fontSize="0.7rem">
                      Cache Savings
                    </Typography>
                    <Typography variant="body2" fontSize="0.75rem" color="success.main">
                      ${(usage.cache_savings || 0).toFixed(4)}
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </>
          )}

          <Divider sx={{ my: 1.5 }} />

          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center' }}>
            Current: Claude API • {config.model}
          </Typography>
        </Box>
      </Menu>
    </>
  );
};

export default LLMConfigDropdown;
