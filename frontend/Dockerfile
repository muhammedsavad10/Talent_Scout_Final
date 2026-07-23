# Stage 1: Build the React Application
FROM node:20-alpine AS build

WORKDIR /app

# Copy dependency mappings
COPY package*.json ./

# Install npm modules
RUN npm ci --legacy-peer-deps

# Copy workspace source files
COPY . .

# Run production compilation build
RUN npm run build

# Stage 2: Serve static files via Nginx
FROM nginx:alpine

# Copy built frontend assets from builder stage
COPY --from=build /app/dist /usr/share/nginx/html

# Overwrite default Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
