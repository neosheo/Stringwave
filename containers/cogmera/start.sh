uwsgi \
    --socket :3032 \
    --wsgi-file app.py \
    --master \
    --threads 2 \
    --callable app \
    --uid cogmera \
    --gid cogmera
