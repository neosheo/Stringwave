cd pipefeeder

uwsgi \
    --socket :3031 \
    --wsgi-file app.py \
    --threads 2 \
    --callable app \
    --uid pipefeeder \
    --gid pipefeeder
