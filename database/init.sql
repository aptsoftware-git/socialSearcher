-- Database initialization script for Social Searcher

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Create user_api_usage table for cost calculation
CREATE TABLE IF NOT EXISTS user_api_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    api_provider VARCHAR(50) NOT NULL, -- 'google_cse', 'scrapecreators', 'claude', etc.
    api_type VARCHAR(50) NOT NULL, -- 'search', 'scraping', 'analysis'
    platform VARCHAR(50), -- 'youtube', 'twitter', 'facebook', 'instagram', 'google', 'web'
    endpoint VARCHAR(100), -- 'search', 'extract', 'analyze', etc.
    api_calls INTEGER DEFAULT 1, -- Number of API calls made
    credits_used INTEGER DEFAULT 0, -- For ScrapeCreators
    tokens_used INTEGER DEFAULT 0, -- For Claude AI
    cached_tokens INTEGER DEFAULT 0, -- For Claude AI with caching
    cost_usd DECIMAL(10, 6) DEFAULT 0.00,
    request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    metadata JSONB -- Additional data like query, result count, etc.
);

-- Create API keys table
CREATE TABLE IF NOT EXISTS user_api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(100) NOT NULL, -- 'Claude API Key', 'Instagram Token', etc.
    encrypted_key TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP
);

-- Create search history table
CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    search_type VARCHAR(50), -- 'social', 'web', 'hybrid'
    results_count INTEGER,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create daily cost summary view
CREATE OR REPLACE VIEW user_daily_cost_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.email,
    DATE(ua.request_timestamp) as usage_date,
    COUNT(DISTINCT CASE WHEN ua.api_type = 'search' THEN ua.id END) as total_searches,
    COUNT(CASE WHEN ua.api_type = 'search' AND ua.platform = 'youtube' THEN 1 END) as youtube_searches,
    COUNT(CASE WHEN ua.api_type = 'search' AND ua.platform = 'twitter' THEN 1 END) as twitter_searches,
    COUNT(CASE WHEN ua.api_type = 'search' AND ua.platform = 'facebook' THEN 1 END) as facebook_searches,
    COUNT(CASE WHEN ua.api_type = 'search' AND ua.platform = 'instagram' THEN 1 END) as instagram_searches,
    COUNT(CASE WHEN ua.api_type = 'search' AND ua.platform = 'google' THEN 1 END) as google_searches,
    COUNT(CASE WHEN ua.api_type = 'scraping' THEN 1 END) as total_scrapings,
    COUNT(CASE WHEN ua.api_type = 'analysis' THEN 1 END) as total_analyses,
    SUM(CASE WHEN ua.api_provider = 'google_cse' THEN ua.api_calls ELSE 0 END) as google_api_calls,
    SUM(CASE WHEN ua.api_provider = 'scrapecreators' THEN ua.credits_used ELSE 0 END) as scrapecreators_credits,
    SUM(CASE WHEN ua.api_provider = 'claude' THEN ua.tokens_used ELSE 0 END) as claude_tokens,
    SUM(ua.cost_usd) as daily_cost_usd
FROM users u
LEFT JOIN user_api_usage ua ON u.id = ua.user_id
GROUP BY u.id, u.username, u.email, DATE(ua.request_timestamp);

-- Create monthly cost summary view
CREATE OR REPLACE VIEW user_monthly_cost_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.email,
    EXTRACT(YEAR FROM ua.request_timestamp) as year,
    EXTRACT(MONTH FROM ua.request_timestamp) as month,
    COUNT(DISTINCT CASE WHEN ua.api_type = 'search' THEN ua.id END) as total_searches,
    COUNT(CASE WHEN ua.api_type = 'search' AND ua.platform = 'youtube' THEN 1 END) as youtube_searches,
    COUNT(CASE WHEN ua.api_type = 'search' AND ua.platform = 'twitter' THEN 1 END) as twitter_searches,
    COUNT(CASE WHEN ua.api_type = 'search' AND ua.platform = 'facebook' THEN 1 END) as facebook_searches,
    COUNT(CASE WHEN ua.api_type = 'search' AND ua.platform = 'instagram' THEN 1 END) as instagram_searches,
    COUNT(CASE WHEN ua.api_type = 'search' AND ua.platform = 'google' THEN 1 END) as google_searches,
    COUNT(CASE WHEN ua.api_type = 'scraping' THEN 1 END) as total_scrapings,
    COUNT(CASE WHEN ua.api_type = 'analysis' THEN 1 END) as total_analyses,
    SUM(CASE WHEN ua.api_provider = 'google_cse' THEN ua.api_calls ELSE 0 END) as google_api_calls,
    SUM(CASE WHEN ua.api_provider = 'scrapecreators' THEN ua.credits_used ELSE 0 END) as scrapecreators_credits,
    SUM(CASE WHEN ua.api_provider = 'claude' THEN ua.tokens_used ELSE 0 END) as claude_tokens,
    SUM(ua.cost_usd) as monthly_cost_usd
FROM users u
LEFT JOIN user_api_usage ua ON u.id = ua.user_id
GROUP BY u.id, u.username, u.email, EXTRACT(YEAR FROM ua.request_timestamp), EXTRACT(MONTH FROM ua.request_timestamp);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_api_usage_user_id ON user_api_usage(user_id);
CREATE INDEX idx_api_usage_timestamp ON user_api_usage(request_timestamp);
CREATE INDEX idx_search_history_user_id ON search_history(user_id);
CREATE INDEX idx_search_history_timestamp ON search_history(created_at);

-- Insert default admin user (password: Admin@123 - CHANGE THIS!)
-- Password hash generated with bcrypt
INSERT INTO users (email, username, password_hash, full_name, is_admin)
VALUES (
    'admin@aptsoftware.in',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5eDWqQhK6V5.W', -- Admin@123
    'System Administrator',
    true
) ON CONFLICT (email) DO NOTHING;

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dbuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dbuser;

COMMENT ON TABLE users IS 'User accounts and authentication';
COMMENT ON TABLE user_api_usage IS 'Track API usage and costs per user';
COMMENT ON TABLE user_api_keys IS 'Encrypted storage for user API keys';
COMMENT ON TABLE search_history IS 'User search query history';
