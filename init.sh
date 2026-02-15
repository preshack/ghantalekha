#!/bin/bash
# WorkClock — Initialization script
# Run after docker-compose up to set up the database

set -e

echo "=================================="
echo "  WorkClock — Database Setup"
echo "=================================="

# Wait for database to be ready
echo "[1/4] Waiting for database..."
sleep 3

# Initialize migrations
echo "[2/4] Initializing migrations..."
docker compose exec web flask db init 2>/dev/null || echo "  Migrations already initialized."

# Generate migration
echo "[3/4] Generating migration..."
docker compose exec web flask db migrate -m "Initial migration" 2>/dev/null || echo "  Migration already exists."

# Apply migration
echo "[4/4] Applying migration..."
docker compose exec web flask db upgrade

# Seed data
echo ""
echo "Seeding test data..."
docker compose exec web flask seed

echo ""
echo "=================================="
echo "  Setup Complete!"
echo "  Visit: http://localhost:8000"
echo "=================================="
