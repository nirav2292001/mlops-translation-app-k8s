# === Stage 1: Build React App ===
FROM node:20-bullseye AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .


RUN npm run build

# === Stage 2: Serve app with Nginx ===
FROM nginx:stable

RUN rm -rf /usr/share/nginx/html/*

ARG REACT_APP_API_URL

ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# Create env.js dynamically
RUN echo "window.env = { REACT_APP_API_URL: \"${REACT_APP_API_URL}\" };" > /usr/share/nginx/html/env.js

COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]