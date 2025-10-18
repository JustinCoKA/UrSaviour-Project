#!/bin/bash

echo "🔄 Running foundational data loader inside Docker container..."

# Copy the data loader script to the container
docker cp load_data_simple.py ursaviour-project-backend-1:/app/load_data_simple.py

# Also copy the CSV file to the container
docker cp data/foundational_dataset_v1.csv ursaviour-project-backend-1:/data/foundational_dataset_v1.csv

echo "📂 Files copied to container. Running data loader..."

# Execute the data loader inside the container
docker exec ursaviour-project-backend-1 python load_data_simple.py

echo "✅ Data loading completed!"
echo ""
echo "🔍 You can verify the data by checking:"
echo "   curl http://localhost:8000/api/v1/debug/counts"
echo "   curl http://localhost:8000/api/v1/products"