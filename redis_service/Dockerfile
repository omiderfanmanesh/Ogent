FROM redis:7-alpine

# Install bash for the entrypoint script
RUN apk add --no-cache bash

# Create directory for the configuration
RUN mkdir -p /usr/local/etc/redis

# Copy the configuration file and entrypoint script
COPY redis.conf /usr/local/etc/redis/redis.conf.template
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Expose Redis port
EXPOSE 6379

# Add health check
HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
    CMD redis-cli ping || exit 1

# Set the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"] 