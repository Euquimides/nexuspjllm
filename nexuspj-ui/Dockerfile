# Use Node.js 18 Alpine as the base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files for dependency installation
COPY package*.json ./

# Install all dependencies
RUN npm install

# Copy application source code
COPY . .

# Set development environment
ENV NODE_ENV=development
ENV PORT=3000
ENV NEXT_TELEMETRY_DISABLED=1

# Expose the Next.js port
EXPOSE 3000

# Start the development server
CMD ["npm", "run", "dev"]
