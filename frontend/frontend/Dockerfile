FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy all source files
COPY . .

# Set build-time environment variable
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Build Next.js application
RUN npm run build

# Expose port
EXPOSE 3000

# Set runtime environment
ENV NODE_ENV=production
ENV PORT=3000

# Start Next.js
CMD ["npm", "start"]
