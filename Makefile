.PHONY: update build up down logs status clean help

# Default target
help:
	@echo "GLM-OCR Makefile"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  update    - Pull latest changes from GitHub"
	@echo "  build     - Build Docker images"
	@echo "  up        - Start containers"
	@echo "  down      - Stop containers"
	@echo "  logs      - Show container logs"
	@echo "  status    - Show container status"
	@echo "  clean     - Remove containers, images, volumes"
	@echo "  all       - Update, build, and start (recommended)"

# Update from GitHub
update:
	@echo "📥 Pulling latest changes..."
	git pull

# Build Docker images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

# Start containers
up:
	@echo "🚀 Starting containers..."
	docker-compose up -d
	@echo "✅ Done! Open http://localhost:8080"

# Stop containers
down:
	@echo "🛑 Stopping containers..."
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

# Container status
status:
	@echo "📊 Container status:"
	@docker-compose ps

# Clean everything
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v --rmi local
	@echo "✅ Clean complete"

# Full update cycle
all: update build up
	@echo "✅ Update complete!"