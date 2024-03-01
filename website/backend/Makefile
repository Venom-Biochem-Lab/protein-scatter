all: serve

serve:
	uvicorn server:app --host 0.0.0.0 --port 8000 --reload

api:
	cd ../frontend && yarn openapi