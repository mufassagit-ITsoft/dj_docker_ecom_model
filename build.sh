#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
```

Then make it executable locally with `chmod a+x build.sh` and push it to your repo.

**B. Update `settings.py`** in your `ecom_model/` folder. You'll need to add a few things:

1. Install the `dj-database-url` and `gunicorn` packages — add them to your `requirements.txt`:
```
gunicorn
dj-database-url
psycopg2-binary