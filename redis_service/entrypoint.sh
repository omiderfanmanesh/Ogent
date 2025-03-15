#!/bin/bash
set -e

# Default values
REDIS_PORT=${REDIS_PORT:-6379}
REDIS_BIND=${REDIS_BIND:-0.0.0.0}
REDIS_MAX_MEMORY=${REDIS_MAX_MEMORY:-256mb}
REDIS_MAX_CLIENTS=${REDIS_MAX_CLIENTS:-10000}
REDIS_AOF_ENABLED=${REDIS_AOF_ENABLED:-yes}
REDIS_RDB_ENABLED=${REDIS_RDB_ENABLED:-yes}

# Create redis.conf from template
cp /usr/local/etc/redis/redis.conf.template /usr/local/etc/redis/redis.conf

# Update configuration with environment variables
sed -i "s/port 6379/port $REDIS_PORT/g" /usr/local/etc/redis/redis.conf
sed -i "s/bind 0.0.0.0/bind $REDIS_BIND/g" /usr/local/etc/redis/redis.conf
sed -i "s/maxmemory 256mb/maxmemory $REDIS_MAX_MEMORY/g" /usr/local/etc/redis/redis.conf
sed -i "s/maxclients 10000/maxclients $REDIS_MAX_CLIENTS/g" /usr/local/etc/redis/redis.conf

# Configure password if provided
if [ ! -z "$REDIS_PASSWORD" ]; then
    echo "requirepass $REDIS_PASSWORD" >> /usr/local/etc/redis/redis.conf
fi

# Configure AOF
if [ "$REDIS_AOF_ENABLED" = "no" ]; then
    sed -i "s/appendonly yes/appendonly no/g" /usr/local/etc/redis/redis.conf
fi

# Configure RDB
if [ "$REDIS_RDB_ENABLED" = "no" ]; then
    sed -i "s/save 900 1/# save 900 1/g" /usr/local/etc/redis/redis.conf
    sed -i "s/save 300 10/# save 300 10/g" /usr/local/etc/redis/redis.conf
    sed -i "s/save 60 10000/# save 60 10000/g" /usr/local/etc/redis/redis.conf
fi

# Execute the main command
exec "$@" 