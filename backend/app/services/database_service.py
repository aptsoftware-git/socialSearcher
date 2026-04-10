"""
Database service for user management and usage tracking.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from loguru import logger
from app.settings import settings


class DatabaseService:
    """Service for database operations."""
    
    def __init__(self):
        """Initialize database connection pool."""
        self.pool: Optional[SimpleConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Create connection pool."""
        try:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=settings.database_host,
                port=settings.database_port,
                database=settings.database_name,
                user=settings.database_user,
                password=settings.database_password
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    def get_connection(self):
        """Get connection from pool."""
        if self.pool:
            return self.pool.getconn()
        raise Exception("Connection pool not initialized")
    
    def return_connection(self, conn):
        """Return connection to pool."""
        if self.pool:
            self.pool.putconn(conn)
    
    # ==================== USER MANAGEMENT ====================
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, email, username, password_hash, full_name, company, profile_image_url,
                           is_active, is_admin, created_at, updated_at, last_login,
                           search_limit, quota_start_date, quota_end_date
                    FROM users 
                    WHERE email = %s
                    """,
                    (email,)
                )
                return cur.fetchone()
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, email, username, password_hash, full_name, company, profile_image_url,
                           is_active, is_admin, created_at, updated_at, last_login,
                           search_limit, quota_start_date, quota_end_date
                    FROM users 
                    WHERE id = %s
                    """,
                    (user_id,)
                )
                return cur.fetchone()
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (for admin)."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT u.id, u.email, u.username, u.full_name, u.company, u.profile_image_url,
                           u.is_active, u.is_admin, u.created_at, u.last_login,
                           u.search_limit, u.quota_start_date, u.quota_end_date,
                           (
                               SELECT COUNT(*)
                               FROM user_api_usage ua
                               WHERE ua.user_id = u.id
                                 AND ua.api_type = 'search'
                                 AND ua.platform IN ('youtube', 'twitter', 'facebook', 'instagram', 'google')
                                 AND (u.quota_start_date IS NULL OR ua.request_timestamp::date >= u.quota_start_date)
                                 AND (u.quota_end_date   IS NULL OR ua.request_timestamp::date <= u.quota_end_date)
                           ) AS searches_used
                    FROM users u
                    ORDER BY u.created_at DESC
                    """
                )
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
        finally:
            if conn:
                self.return_connection(conn)
    
    def create_user(self, email: str, username: str, password_hash: str, 
                   full_name: Optional[str] = None, company: Optional[str] = None, is_admin: bool = False) -> Optional[Dict[str, Any]]:
        """Create new user."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO users (email, username, password_hash, full_name, company, is_admin)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, email, username, full_name, company, profile_image_url, is_active, is_admin, created_at
                    """,
                    (email, username, password_hash, full_name, company, is_admin)
                )
                user = cur.fetchone()
                conn.commit()
                return user
        except psycopg2.IntegrityError as e:
            logger.error(f"User already exists: {e}")
            if conn:
                conn.rollback()
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                self.return_connection(conn)
    
    def update_user(self, user_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update user fields."""
        conn = None
        try:
            # Build dynamic update query
            allowed_fields = ['email', 'username', 'password_hash', 'full_name', 'company',
                              'profile_image_url', 'is_active', 'search_limit',
                              'quota_start_date', 'quota_end_date']
            update_fields = []
            values = []
            
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    update_fields.append(f"{field} = %s")
                    values.append(value)

            # Handle explicit NULL clears (e.g., removing quota)
            null_fields = kwargs.get('_null_fields', [])
            for field in null_fields:
                if field in allowed_fields:
                    update_fields.append(f"{field} = NULL")
            
            if not update_fields:
                return None
            
            values.append(user_id)
            
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"""
                    UPDATE users 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                    RETURNING id, email, username, full_name, company, profile_image_url, is_active, is_admin,
                              created_at, updated_at, search_limit, quota_start_date, quota_end_date
                    """,
                    values
                )
                user = cur.fetchone()
                conn.commit()
                return user
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                self.return_connection(conn)
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                    (user_id,)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False
        finally:
            if conn:
                self.return_connection(conn)
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete by setting is_active = false)."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET is_active = false WHERE id = %s",
                    (user_id,)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.return_connection(conn)
    
    # ==================== USAGE TRACKING ====================
    
    def log_api_usage(self, user_id: int, api_provider: str, api_type: str,
                     platform: Optional[str] = None, endpoint: Optional[str] = None,
                     api_calls: int = 1, credits_used: int = 0, tokens_used: int = 0,
                     cached_tokens: int = 0, cost_usd: float = 0.0,
                     response_time_ms: Optional[int] = None, success: bool = True,
                     error_message: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """Log API usage for cost tracking."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO user_api_usage 
                    (user_id, api_provider, api_type, platform, endpoint, api_calls, 
                     credits_used, tokens_used, cached_tokens, cost_usd, response_time_ms, 
                     success, error_message, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, api_provider, api_type, platform, endpoint, api_calls,
                     credits_used, tokens_used, cached_tokens, cost_usd, response_time_ms,
                     success, error_message, psycopg2.extras.Json(metadata) if metadata else None)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging API usage: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_user_daily_usage(self, user_id: int, year: int, month: int) -> List[Dict[str, Any]]:
        """Get daily usage breakdown for a user in a specific month."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT 
                        DATE(request_timestamp) as usage_date,
                        COUNT(DISTINCT CASE WHEN api_type = 'search' THEN id END) as total_searches,
                        COUNT(CASE WHEN api_type = 'search' AND platform = 'youtube' THEN 1 END) as youtube_searches,
                        COUNT(CASE WHEN api_type = 'search' AND platform = 'twitter' THEN 1 END) as twitter_searches,
                        COUNT(CASE WHEN api_type = 'search' AND platform = 'facebook' THEN 1 END) as facebook_searches,
                        COUNT(CASE WHEN api_type = 'search' AND platform = 'instagram' THEN 1 END) as instagram_searches,
                        COUNT(CASE WHEN api_type = 'search' AND platform = 'google' THEN 1 END) as google_searches,
                        COUNT(CASE WHEN api_type = 'scraping' THEN 1 END) as total_scrapings,
                        COUNT(CASE WHEN api_type = 'scraping' AND api_provider IN ('scrapecreators', 'google_cse') THEN 1 END) as paid_scrapings,
                        COUNT(CASE WHEN api_type = 'scraping' AND api_provider = 'internal' THEN 1 END) as free_scrapings,
                        COUNT(CASE WHEN api_type = 'analysis' THEN 1 END) as total_analyses,
                        COALESCE(SUM(CASE WHEN api_provider = 'google_cse' THEN api_calls ELSE 0 END), 0)::INTEGER as google_api_calls,
                        COALESCE(SUM(CASE WHEN api_provider = 'scrapecreators' THEN credits_used ELSE 0 END), 0)::INTEGER as scrapecreators_credits,
                        COALESCE(SUM(CASE WHEN api_provider = 'claude' THEN tokens_used ELSE 0 END), 0)::INTEGER as claude_tokens,
                        COALESCE(SUM(cost_usd), 0.0)::FLOAT as daily_cost_usd
                    FROM user_api_usage
                    WHERE user_id = %s 
                      AND EXTRACT(YEAR FROM request_timestamp) = %s 
                      AND EXTRACT(MONTH FROM request_timestamp) = %s
                    GROUP BY DATE(request_timestamp)
                    ORDER BY DATE(request_timestamp)
                    """,
                    (user_id, year, month)
                )
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Error getting user daily usage: {e}")
            return []
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_user_monthly_summary(self, user_id: int, year: int, month: int) -> Optional[Dict[str, Any]]:
        """Get monthly summary for a user."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT 
                        COUNT(DISTINCT CASE WHEN api_type = 'search' THEN id END) as total_searches,
                        COUNT(CASE WHEN api_type = 'search' AND platform = 'youtube' THEN 1 END) as youtube_searches,
                        COUNT(CASE WHEN api_type = 'search' AND platform = 'twitter' THEN 1 END) as twitter_searches,
                        COUNT(CASE WHEN api_type = 'search' AND platform = 'facebook' THEN 1 END) as facebook_searches,
                        COUNT(CASE WHEN api_type = 'search' AND platform = 'instagram' THEN 1 END) as instagram_searches,
                        COUNT(CASE WHEN api_type = 'search' AND platform = 'google' THEN 1 END) as google_searches,
                        COUNT(CASE WHEN api_type = 'scraping' THEN 1 END) as total_scrapings,
                        COUNT(CASE WHEN api_type = 'scraping' AND api_provider IN ('scrapecreators', 'google_cse') THEN 1 END) as paid_scrapings,
                        COUNT(CASE WHEN api_type = 'scraping' AND api_provider = 'internal' THEN 1 END) as free_scrapings,
                        COUNT(CASE WHEN api_type = 'analysis' THEN 1 END) as total_analyses,
                        COALESCE(SUM(CASE WHEN api_provider = 'google_cse' THEN api_calls ELSE 0 END), 0)::INTEGER as google_api_calls,
                        COALESCE(SUM(CASE WHEN api_provider = 'scrapecreators' THEN credits_used ELSE 0 END), 0)::INTEGER as scrapecreators_credits,
                        COALESCE(SUM(CASE WHEN api_provider = 'claude' THEN tokens_used ELSE 0 END), 0)::INTEGER as claude_tokens,
                        COALESCE(SUM(cost_usd), 0.0)::FLOAT as monthly_cost_usd
                    FROM user_api_usage
                    WHERE user_id = %s 
                      AND EXTRACT(YEAR FROM request_timestamp) = %s 
                      AND EXTRACT(MONTH FROM request_timestamp) = %s
                    """,
                    (user_id, year, month)
                )
                return cur.fetchone()
        except Exception as e:
            logger.error(f"Error getting user monthly summary: {e}")
            return None
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_user_total_cost(self, user_id: int) -> float:
        """Get total cost for a user (all time)."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COALESCE(SUM(cost_usd), 0) FROM user_api_usage WHERE user_id = %s",
                    (user_id,)
                )
                result = cur.fetchone()
                return float(result[0]) if result else 0.0
        except Exception as e:
            logger.error(f"Error getting user total cost: {e}")
            return 0.0
        finally:
            if conn:
                self.return_connection(conn)

    def log_search_history(self, user_id: int, query: str, search_type: str = 'social') -> bool:
        """Log a search request to search_history (one row per search = quota unit)."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO search_history (user_id, query, search_type) VALUES (%s, %s, %s)",
                    (user_id, query, search_type)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging search history: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.return_connection(conn)

    def get_user_quota_status(self, user_id: int) -> Dict[str, Any]:
        """Get current quota status for a user."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get quota settings
                cur.execute(
                    "SELECT search_limit, quota_start_date, quota_end_date FROM users WHERE id = %s",
                    (user_id,)
                )
                user = cur.fetchone()
                if not user:
                    return {'has_limit': False, 'searches_used': 0, 'search_limit': None,
                            'quota_start_date': None, 'quota_end_date': None,
                            'total_scrapings': 0, 'total_analyses': 0,
                            'percentage': 0.0, 'period_label': '', 'period_expired': False, 'daily_breakdown': []}

                search_limit = user['search_limit']
                start_date = user['quota_start_date']
                end_date = user['quota_end_date']

                # Count searches from user_api_usage (sum of per-platform rows) in quota period
                if start_date and end_date:
                    cur.execute(
                        """
                        SELECT COUNT(*) as searches_used
                        FROM user_api_usage
                        WHERE user_id = %s
                          AND api_type = 'search'
                          AND platform IN ('youtube', 'twitter', 'facebook', 'instagram', 'google')
                          AND request_timestamp::date >= %s AND request_timestamp::date <= %s
                        """,
                        (user_id, start_date, end_date)
                    )
                else:
                    cur.execute(
                        """
                        SELECT COUNT(*) as searches_used
                        FROM user_api_usage
                        WHERE user_id = %s
                          AND api_type = 'search'
                          AND platform IN ('youtube', 'twitter', 'facebook', 'instagram', 'google')
                        """,
                        (user_id,)
                    )
                searches_used = cur.fetchone()['searches_used']

                # Count scrapings and analyses in quota period
                if start_date and end_date:
                    cur.execute(
                        """
                        SELECT
                            COUNT(CASE WHEN api_type = 'scraping' THEN 1 END) as total_scrapings,
                            COUNT(CASE WHEN api_type = 'analysis' THEN 1 END) as total_analyses
                        FROM user_api_usage
                        WHERE user_id = %s AND request_timestamp::date >= %s AND request_timestamp::date <= %s
                        """,
                        (user_id, start_date, end_date)
                    )
                else:
                    cur.execute(
                        """
                        SELECT
                            COUNT(CASE WHEN api_type = 'scraping' THEN 1 END) as total_scrapings,
                            COUNT(CASE WHEN api_type = 'analysis' THEN 1 END) as total_analyses
                        FROM user_api_usage WHERE user_id = %s
                        """,
                        (user_id,)
                    )
                totals = cur.fetchone()

                # Daily breakdown in quota period (no cost)
                if start_date and end_date:
                    cur.execute(
                        """
                        SELECT
                            DATE(request_timestamp) as usage_date,
                            COUNT(DISTINCT CASE WHEN api_type = 'search' THEN id END) as total_searches,
                            COUNT(CASE WHEN api_type = 'search' AND platform = 'youtube' THEN 1 END) as youtube_searches,
                            COUNT(CASE WHEN api_type = 'search' AND platform = 'twitter' THEN 1 END) as twitter_searches,
                            COUNT(CASE WHEN api_type = 'search' AND platform = 'facebook' THEN 1 END) as facebook_searches,
                            COUNT(CASE WHEN api_type = 'search' AND platform = 'instagram' THEN 1 END) as instagram_searches,
                            COUNT(CASE WHEN api_type = 'search' AND platform = 'google' THEN 1 END) as google_searches,
                            COUNT(CASE WHEN api_type = 'scraping' THEN 1 END) as total_scrapings,
                            COUNT(CASE WHEN api_type = 'scraping' AND api_provider IN ('scrapecreators', 'google_cse') THEN 1 END) as paid_scrapings,
                            COUNT(CASE WHEN api_type = 'scraping' AND api_provider = 'internal' THEN 1 END) as free_scrapings,
                            COUNT(CASE WHEN api_type = 'analysis' THEN 1 END) as total_analyses
                        FROM user_api_usage
                        WHERE user_id = %s AND request_timestamp::date >= %s AND request_timestamp::date <= %s
                        GROUP BY DATE(request_timestamp)
                        ORDER BY DATE(request_timestamp)
                        """,
                        (user_id, start_date, end_date)
                    )
                else:
                    cur.execute(
                        """
                        SELECT
                            DATE(request_timestamp) as usage_date,
                            COUNT(DISTINCT CASE WHEN api_type = 'search' THEN id END) as total_searches,
                            COUNT(CASE WHEN api_type = 'search' AND platform = 'youtube' THEN 1 END) as youtube_searches,
                            COUNT(CASE WHEN api_type = 'search' AND platform = 'twitter' THEN 1 END) as twitter_searches,
                            COUNT(CASE WHEN api_type = 'search' AND platform = 'facebook' THEN 1 END) as facebook_searches,
                            COUNT(CASE WHEN api_type = 'search' AND platform = 'instagram' THEN 1 END) as instagram_searches,
                            COUNT(CASE WHEN api_type = 'search' AND platform = 'google' THEN 1 END) as google_searches,
                            COUNT(CASE WHEN api_type = 'scraping' THEN 1 END) as total_scrapings,
                            COUNT(CASE WHEN api_type = 'scraping' AND api_provider IN ('scrapecreators', 'google_cse') THEN 1 END) as paid_scrapings,
                            COUNT(CASE WHEN api_type = 'scraping' AND api_provider = 'internal' THEN 1 END) as free_scrapings,
                            COUNT(CASE WHEN api_type = 'analysis' THEN 1 END) as total_analyses
                        FROM user_api_usage
                        WHERE user_id = %s
                        GROUP BY DATE(request_timestamp)
                        ORDER BY DATE(request_timestamp)
                        """,
                        (user_id,)
                    )
                daily = [dict(row) for row in cur.fetchall()]

                percentage = 0.0
                if search_limit and search_limit > 0:
                    percentage = min(100.0, round(searches_used / search_limit * 100, 1))

                period_label = ''
                if start_date and end_date:
                    period_label = f"{start_date.strftime('%d %b %Y')} – {end_date.strftime('%d %b %Y')}"

                from datetime import date as _date
                period_expired = (end_date is not None and _date.today() > end_date)

                return {
                    'has_limit': search_limit is not None,
                    'search_limit': search_limit,
                    'quota_start_date': start_date,
                    'quota_end_date': end_date,
                    'searches_used': int(searches_used),
                    'total_scrapings': int(totals['total_scrapings']),
                    'total_analyses': int(totals['total_analyses']),
                    'percentage': percentage,
                    'period_label': period_label,
                    'period_expired': period_expired,
                    'daily_breakdown': daily,
                }
        except Exception as e:
            logger.error(f"Error getting quota status: {e}")
            return {'has_limit': False, 'searches_used': 0, 'search_limit': None,
                    'quota_start_date': None, 'quota_end_date': None,
                    'total_scrapings': 0, 'total_analyses': 0,
                    'percentage': 0.0, 'period_label': '', 'period_expired': False, 'daily_breakdown': []}
        finally:
            if conn:
                self.return_connection(conn)
    
    def __del__(self):
        """Cleanup connection pool."""
        if self.pool:
            self.pool.closeall()


# Global database service instance
db_service = DatabaseService()
