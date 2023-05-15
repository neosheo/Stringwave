service cron start

uwsgi \
    --socket :3032 \
    --wsgi-file app.py \
    --threads 2 \
    --callable app \
    --uid cogmera \
    --gid cogmera
