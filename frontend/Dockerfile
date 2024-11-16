# Base image
FROM node:20-alpine as builder

# Set working directory
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install --frozen-lockfile

# Copy source files
COPY . .

# Build the application
RUN npm run build

# Runtime base image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy built files
COPY --from=builder /app/.next /app/.next
COPY package.json package-lock.json ./

# Install only production dependencies
RUN npm install --frozen-lockfile --production

# Expose the application port
EXPOSE 3000

# Healthcheck script
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --spider http://localhost:3000 || exit 1

# Command to run Next.js
CMD ["npm", "start"]