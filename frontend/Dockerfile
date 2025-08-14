# === Stage 1: Build React App ===
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci --silent

# Copy source code
COPY . .

# Build the application
RUN npm run build

# === Stage 2: Serve app with Nginx ===
FROM nginx:alpine

# Copy nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy the build output from the builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Set environment variables with defaults
ENV REACT_APP_API_URL=http://localhost:8000

# Create a script to generate env.js with runtime environment variables
RUN echo '#!/bin/sh \
set -e \
\
# Create or overwrite env.js with the current environment variables \
echo "window.env = { \
  REACT_APP_API_URL: \"'"$REACT_APP_API_URL"'" \
};" > /usr/share/nginx/html/env.js \
\
# Start nginx \
exec "$@"' > /docker-entrypoint.sh \
    && chmod +x /docker-entrypoint.sh

# Expose port 80
EXPOSE 80

# Use the custom entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]

# Start nginx
CMD ["nginx", "-g", "daemon off;"]