# Redis Service for Ogent

This directory contains the Redis configuration for the Ogent project.

## Overview

Redis is used in the Ogent project as:
- A message broker for communication between services
- A cache for storing agent information
- A storage for command results and progress updates

## Configuration

The Redis service is configured with:
- Persistence enabled (both RDB and AOF)
- Memory limit of 256MB with LRU eviction policy
- Network binding to all interfaces (0.0.0.0)
- Default port 6379

## Files

- `Dockerfile`: Custom Docker image definition for Redis
- `redis.conf`: Custom Redis configuration file template
- `entrypoint.sh`: Script to generate the final configuration from environment variables
- `docker-compose.yml`: Standalone Docker Compose file for running Redis
- `.env`: Environment variables for Redis configuration
- `README.md`: This documentation file

## Environment Variables

The following environment variables can be used to customize Redis:

| Variable | Default | Description |
|----------|---------|-------------|
| REDIS_PORT | 6379 | Port Redis listens on |
| REDIS_BIND | 0.0.0.0 | Network interfaces Redis binds to |
| REDIS_MAX_MEMORY | 256mb | Maximum memory Redis can use |
| REDIS_MAX_CLIENTS | 10000 | Maximum number of client connections |
| REDIS_PASSWORD | (none) | Password for Redis authentication |
| REDIS_AOF_ENABLED | yes | Enable/disable append-only file persistence |
| REDIS_RDB_ENABLED | yes | Enable/disable RDB snapshots |

## Usage

### Building the Image

```bash
docker build -t ogent-redis .
```

### Running Redis Standalone

```bash
# Using docker run
docker run -d --name ogent-redis -p 6379:6379 -v redis-data:/data ogent-redis

# Using docker-compose
docker-compose up -d
```

### Using with Docker Compose

The Redis service is included in the main `docker-compose.yml` file at the project root.

## Customization

To customize Redis configuration:
1. Edit the `.env` file with your desired settings
2. Rebuild the Docker image
3. Restart the service

## Security

By default, Redis is configured without password protection. For production use:
1. Set the `REDIS_PASSWORD` environment variable
2. Update the connection URLs in the controller and agent services

## Data Persistence

Redis data is stored in a Docker volume named `redis-data`. This ensures data persists across container restarts.

## Monitoring

To monitor Redis:

```bash
# Connect to Redis CLI
docker exec -it ogent-redis redis-cli

# Check Redis info
INFO

# Monitor commands in real-time
MONITOR
``` 