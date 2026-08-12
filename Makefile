.PHONY: install backend frontend run teams

install:
	pip install -r requirements.txt --force-reinstall --no-cache-dir

backend:
	uvicorn src.api.main:app --port 8000 --reload

frontend:
	cd src/frontend && python -m http.server 3000

run:
	(uvicorn src.api.main:app --port 8000 --reload &) && \
	cd src/frontend && python -m http.server 3000

teams:
	python -m scripts.update.update_teams
