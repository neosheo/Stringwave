FROM python:3.11.3-slim-bullseye

RUN apt-get update && apt-get install gcc -y

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN rm requirements.txt

RUN groupadd -r --gid 1000 pipefeeder && useradd -r --uid 1000 -g pipefeeder pipefeeder
RUN chsh -s /usr/sbin/nologin root

COPY app.py ./pipefeeder/
COPY pipefeeder.py ./pipefeeder/
COPY webapp/ ./pipefeeder/webapp/
COPY backup/ ./pipefeeder/backup/
COPY start_uwsgi.sh ./pipefeeder/
COPY run.sh ./pipefeeder/

RUN touch /pipefeeder/backup/subs.txt /pipefeeder/.urls
RUN chown -R pipefeeder:pipefeeder /pipefeeder/webapp /pipefeeder/.urls /pipefeeder/backup /pipefeeder/app.py /pipefeeder/start_uwsgi.sh
RUN echo "30 3 * * * cd /pipefeeder && ./run.sh | crontab -"

ENTRYPOINT [ "sh", "./pipefeeder/start_uwsgi.sh" ]
