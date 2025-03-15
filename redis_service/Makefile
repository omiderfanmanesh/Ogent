.PHONY: build run stop clean logs shell info

# Default values
IMAGE_NAME ?= ogent-redis
CONTAINER_NAME ?= ogent-redis
PORT ?= 6379

# Build the Redis Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Run Redis container
run:
	docker run -d --name $(CONTAINER_NAME) \
		-p $(PORT):6379 \
		-v redis-data:/data \
		--env-file .env \
		$(IMAGE_NAME)

# Run using docker-compose
up:
	docker-compose up -d

# Stop and remove the Redis container
stop:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

# Stop using docker-compose
down:
	docker-compose down

# Clean up (stop container and remove image)
clean: stop
	docker rmi $(IMAGE_NAME) || true

# View Redis logs
logs:
	docker logs -f $(CONTAINER_NAME)

# Open a shell in the Redis container
shell:
	docker exec -it $(CONTAINER_NAME) sh

# Connect to Redis CLI
cli:
	docker exec -it $(CONTAINER_NAME) redis-cli

# Show Redis info
info:
	docker exec -it $(CONTAINER_NAME) redis-cli info

# Monitor Redis commands
monitor:
	docker exec -it $(CONTAINER_NAME) redis-cli monitor

# Help command
help:
	@echo "Redis Service Management Commands:"
	@echo "  make build     - Build the Redis Docker image"
	@echo "  make run       - Run Redis container"
	@echo "  make up        - Run using docker-compose"
	@echo "  make stop      - Stop and remove the Redis container"
	@echo "  make down      - Stop using docker-compose"
	@echo "  make clean     - Clean up (stop container and remove image)"
	@echo "  make logs      - View Redis logs"
	@echo "  make shell     - Open a shell in the Redis container"
	@echo "  make cli       - Connect to Redis CLI"
	@echo "  make info      - Show Redis info"
	@echo "  make monitor   - Monitor Redis commands"
	@echo "  make help      - Show this help message" 