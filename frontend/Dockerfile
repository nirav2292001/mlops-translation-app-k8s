# === Stage 1: Build React App ===
FROM node:20-bullseye AS builder

WORKDIR /app

# Copy package files first for better caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --silent

# Copy the rest of the application
COPY . .

# Build the application
RUN npm run build

# === Stage 2: Serve app with Nginx ===
FROM nginx:stable-alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy the build output from the builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Environment variables for runtime configuration
ENV PORT=80
ENV HOST=0.0.0.0

# Create a script to generate env.js with runtime environment variables
RUN echo '#!/bin/sh \n\
# Create directory if it doesn\'t exist \n\
mkdir -p /usr/share/nginx/html \n\
# Create or overwrite env.js with the current environment variables \n\
echo "window.env = { \
  REACT_APP_API_URL: \"${REACT_APP_API_URL:-http://localhost:8000}\" \
};" > /usr/share/nginx/html/env.js \n\
# Start nginx \n\
exec "$@"' > /docker-entrypoint.sh \
    && chmod +x /docker-entrypoint.sh

# Expose the port the app runs on
EXPOSE 80

# Use the custom entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]

# Start nginx
CMD ["nginx", "-g", "daemon off;"]