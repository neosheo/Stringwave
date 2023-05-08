FROM python:3.11.3-slim-bullseye

WORKDIR /pipefeeder

RUN apt-get update && apt-get upgrade -y
RUN apt-get install gcc cron -y

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN rm requirements.txt

RUN groupadd -r --gid 1000 pipefeeder && useradd -r --uid 1000 -g pipefeeder pipefeeder
RUN chsh --shell /usr/sbin/nologin root

COPY app.py .
COPY pipefeeder.py .
COPY webapp/ ./webapp/
COPY backup/ ./backup/
COPY upload.py .
COPY start.sh .
COPY run.sh .

RUN touch /pipefeeder/backup/subs.txt /pipefeeder/.urls
RUN chown -R pipefeeder:pipefeeder /pipefeeder/
RUN echo "30 3 * * * cd /pipefeeder && ./run.sh | crontab -u pipefeeder -"

ENTRYPOINT [ "sh", "./start.sh" ]
