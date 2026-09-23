.PHONY: install seed dev backend frontend test docker-up docker-down clean

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

seed:
	python3 scripts/generate_data.py

train:
	python3 scripts/train_models.py --force

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

dev:
	@echo "Run 'make backend' and 'make frontend' in separate terminals"

test:
	cd backend && pytest -v

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/dist
