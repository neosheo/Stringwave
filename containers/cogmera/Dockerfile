FROM python:3.11.3-slim-bullseye

RUN apt-get update && apt-get install gcc cron -y

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

RUN apt-get install -y curl

RUN groupadd -r --gid 1000 cogmera && useradd -r --uid 1000 -g cogmera cogmera
RUN chsh -s /usr/sbin/nologin root

COPY app.py ./cogmera/
COPY cogmera.py ./cogmera/
COPY webapp/ ./cogmera/webapp/
COPY start_uwsgi.sh ./cogmera/
COPY run.py ./cogmera/
COPY run.sh ./cogmera/

RUN touch /cogmera/webapp/instance/configs.db
RUN chown -R cogmera:cogmera /cogmera/
RUN echo "0 3 * * * cd /cogmera && ./run.sh" | crontab -

ENTRYPOINT [ "sh", "./cogmera/start_uwsgi.sh" ]
