Flower
flower -A bootstrap --port=5555
Run Worker
celery -A consumer worker --loglevel=INFO -n worker1.%h

Kombu Example
http://docs.celeryproject.org/projects/kombu/en/latest/userguide/examples.html
