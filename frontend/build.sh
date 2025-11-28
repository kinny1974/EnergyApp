#!/bin/bash

# Frontend Build Script for Railway Deployment

echo "🚀 Building Energy App Frontend..."

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the application
echo "🏗️ Building application..."
npm run build

echo "✅ Frontend build completed successfully!"
echo "📁 Build output: dist/"