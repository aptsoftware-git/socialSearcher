#!/bin/bash
# SSL certificate auto-renewal script for tigerosint.aptsoftware.in
# Stops nginx, renews cert if needed, copies files, restarts nginx.

set -e

DOMAIN="tigerosint.aptsoftware.in"
SSL_DIR="/home/ubuntu/socialSearcher/nginx/ssl"
LOG_FILE="/var/log/ssl_renew.log"
NGINX_CONTAINER="socialSearcher_nginx"

echo "$(date): Checking certificate renewal for ${DOMAIN}" >> "$LOG_FILE"

# Stop nginx to free port 80 for standalone challenge
docker stop "$NGINX_CONTAINER" >> "$LOG_FILE" 2>&1

# Attempt renewal (certbot skips if cert is not yet within 30 days of expiry)
if certbot renew --quiet >> "$LOG_FILE" 2>&1; then
    # Copy renewed cert and key to nginx ssl directory
    cp "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" "${SSL_DIR}/cert.pem"
    cp "/etc/letsencrypt/live/${DOMAIN}/privkey.pem"   "${SSL_DIR}/key.pem"
    chown ubuntu:ubuntu "${SSL_DIR}/cert.pem" "${SSL_DIR}/key.pem"
    echo "$(date): Certificate renewed and deployed successfully." >> "$LOG_FILE"
else
    echo "$(date): Certificate renewal failed." >> "$LOG_FILE"
fi

# Always restart nginx regardless of renewal outcome
docker start "$NGINX_CONTAINER" >> "$LOG_FILE" 2>&1

echo "$(date): nginx restarted." >> "$LOG_FILE"
