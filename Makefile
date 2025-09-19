env:
	cp .env.example .env

build:
	docker build -t file-storage:latest . && docker compose up --build -d && docker compose logs -f

up:
	docker compose up -d

stop:
	docker compose stop
