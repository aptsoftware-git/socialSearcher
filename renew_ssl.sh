#!/bin/bash
# SSL certificate auto-renewal script for tigerosint.aptsoftware.in
# Stops nginx, renews cert if needed, copies files, restarts nginx.

set -e

DOMAIN="tigerosint.aptsoftware.in"
SSL_DIR="/home/ubuntu/socialSearcher/nginx/ssl"
LOG_FILE="/var/log/ssl_renew.log"
NGINX_CONTAINER="socialSearcher_nginx"

echo "$(date): Checking certificate renewal for ${DOMAIN}" >> "$LOG_FILE"

# Renew using webroot - nginx stays running, no downtime needed.
# Certbot writes challenge files to the host path, which is bind-mounted
# into the nginx container at /var/www/certbot.
WEBROOT="/home/ubuntu/socialSearcher/nginx/certbot"
if certbot renew --quiet --webroot -w "$WEBROOT" >> "$LOG_FILE" 2>&1; then
    # Copy renewed cert and key to nginx ssl directory
    cp "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" "${SSL_DIR}/cert.pem"
    cp "/etc/letsencrypt/live/${DOMAIN}/privkey.pem"   "${SSL_DIR}/key.pem"
    chown ubuntu:ubuntu "${SSL_DIR}/cert.pem" "${SSL_DIR}/key.pem"
    # Reload nginx gracefully (no stop/start needed)
    docker exec "$NGINX_CONTAINER" nginx -s reload >> "$LOG_FILE" 2>&1
    echo "$(date): Certificate renewed and nginx reloaded successfully." >> "$LOG_FILE"
else
    echo "$(date): Certificate renewal failed or not yet due." >> "$LOG_FILE"
fi

echo "$(date): Renewal check complete." >> "$LOG_FILE"
