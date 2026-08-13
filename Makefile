.PHONY: install backend frontend run teams update-full update-latest

install:
	pip install -r requirements.txt --force-reinstall --no-cache-dir

backend:
	uvicorn src.api.main:app --port 8000 --reload

frontend:
	cd src/frontend && python -m http.server 3000

run:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

teams:
	python -m scripts.update.update_teams

update-full:
	python -m scripts.update.update_database full

update-latest:
	python -m scripts.update.update_database latest
