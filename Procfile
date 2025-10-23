web: gunicorn enhanced_interactive_demo:app --bind 0.0.0.0:$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker
worker: celery -A backend.main worker --loglevel=info