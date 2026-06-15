FROM node:20-alpine AS build

WORKDIR /app

# Expose Railway environment variables to the React build process
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Install dependencies (using npm install instead of ci to be more forgiving)
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
# Setting CI=false prevents the build from failing on ESLint warnings
RUN CI=false npm run build

# Production server
FROM node:20-alpine

WORKDIR /app
RUN npm install -g serve

# Copy built assets
COPY --from=build /app/build ./build

# Railway provides the PORT environment variable
ENV PORT=3000
EXPOSE ${PORT}

# Start the server
CMD serve -s build -l ${PORT}
