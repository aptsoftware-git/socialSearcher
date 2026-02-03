# Multi-stage build for React Frontend

# Stage 1: Build the application
FROM node:20-slim AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Manually install Rollup binary to fix optional dependency bug
RUN npm install --save-optional @rollup/rollup-linux-x64-gnu

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
