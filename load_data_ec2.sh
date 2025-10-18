#!/bin/bash

echo "🔄 Loading foundational data into Docker container on EC2..."

# First, copy the data loader script into the container
docker cp load_data_simple.py ursaviour-api-1:/app/load_data_simple.py

# Copy the CSV file to the container
docker cp data/foundational_dataset_v1.csv ursaviour-api-1:/app/foundational_dataset_v1.csv

echo "📂 Files copied to container. Running data loader..."

# Execute the data loader inside the container
docker exec ursaviour-api-1 python load_data_simple.py

echo ""
echo "🔍 Verifying the results..."

# Check counts after loading
curl -s http://localhost:8000/api/v1/products/debug/counts | jq '.'

echo ""
echo "🔍 Checking product API..."

# Check if products are now available
curl -s http://localhost:8000/api/v1/products/ | jq '.total_count'

echo ""
echo "✅ Data loading process completed!"