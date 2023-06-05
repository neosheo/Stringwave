FROM python:3.11.3-slim-bullseye

WORKDIR /pipefeeder

RUN apt-get update && apt-get upgrade -y
RUN apt-get install gcc -y

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN rm requirements.txt

RUN groupadd -r --gid 1000 pipefeeder && useradd -r --uid 1000 -g pipefeeder pipefeeder
RUN chsh --shell /usr/sbin/nologin root

COPY app.py .
COPY pipefeeder.py .
COPY bad_words.py .
COPY webapp/ ./webapp/
COPY backup/ ./backup/
COPY upload.py .
COPY start.sh .
COPY run.sh .

RUN touch /pipefeeder/backup/subs.txt /pipefeeder/.urls /pipefeeder/webapp/static/upload_status
RUN chown -R pipefeeder:pipefeeder /pipefeeder/

ENTRYPOINT [ "bash", "./start.sh" ]
