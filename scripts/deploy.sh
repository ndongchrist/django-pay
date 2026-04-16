#!/bin/bash

# Build and start the Docker containers

docker compose down
docker compose up -d

echo "Continous Deployment Completed successfully." 