#!/bin/bash

set -e

echo "🔹 Stopping existing containers..."
docker compose down

echo "🔹 Building images..."
docker compose build

echo "🔹 Starting containers..."
docker compose up -d


