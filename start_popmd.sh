#!/bin/bash

# 1. Load environment variables from the .env file
echo "Loading environment variables..."
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo ".env file does not exist. Please create it and add POPM_BTC_PRIVKEY and EVM_RIVKEY configurations."
  exit 1
fi

# 2. Check and start the Docker service
echo "Checking Docker service..."
if ! service docker status > /dev/null; then
  echo "Starting Docker service..."
  sudo service docker start
fi

# 3. Download dependencies and build the project
echo "Checking if the project needs to be built..."
if [ ! -f "./bin/popmd" ] || [ ! -f "./bin/bfgd" ] || [ ! -f "./bin/bssd" ]; then
  echo "Building the project..."
  make deps    # Download and install dependencies
  make install # Build the binary files
else
  echo "Binary files already exist, skipping the build step."
fi

# 4. Build the Docker image
if [[ "$(docker images -q hemi-sync-container 2> /dev/null)" == "" ]]; then
  echo "Building Docker image..."
  if ! docker build -t hemi-sync-container ./sync; then
    echo "Docker image build failed, exiting."
    exit 1
  fi
else
  echo "Docker image already exists, skipping the build step."
fi

# 5. Start the popmd service
echo "Starting popmd service..."
docker run --rm --env-file .env hemi-sync-container &
./bin/popmd &
if [ $? -ne 0 ]; then
  echo "Failed to start popmd service, exiting."
  exit 1
fi

# 6. Keep the script running
wait