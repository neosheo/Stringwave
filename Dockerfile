FROM python:3.11.3-slim-bullseye

WORKDIR /stringwave

RUN apt-get update && apt-get upgrade -y 
RUN apt-get install ffmpeg icecast2 ezstream gcc tmux procps sqlite3 -y
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN rm requirements.txt

RUN groupadd -r --gid 1000 stringwave && useradd -r --uid 1000 -g stringwave stringwave
RUN chsh --shell /usr/sbin/nologin root

COPY radio/ ./radio/
COPY scripts/ ./scripts/
COPY webapp/ ./webapp/
COPY logs/ ./logs/
COPY config/icecast.xml ./config/
COPY config/ezstream.xml ./config/
COPY src/ ./src/
COPY app.py .
COPY start.sh .

RUN touch /stringwave/logs/cogmera.log /stringwave/logs/pipefeeder.log /var/log/icecast2/access.log /var/log/icecast2/error.log
RUN echo 99999 > /stringwave/.pid
RUN chown -R stringwave:stringwave /stringwave/ /var/log/icecast2/access.log /var/log/icecast2/error.log
RUN gcc /stringwave/src/monitor_port.c -o /bin/monitor_port

ENTRYPOINT ["bash", "./start.sh"]
