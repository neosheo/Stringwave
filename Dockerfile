FROM python:3.11.3-slim-bullseye

RUN apt-get update && apt-get upgrade -y && apt-get install ffmpeg icecast2 ezstream gcc tmux procps -y
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN rm requirements.txt

RUN groupadd -r --gid 1000 stringwave && useradd -r --uid 1000 -g stringwave stringwave
RUN chsh --shell /usr/sbin/nologin root

COPY radio/ ./stringwave/radio/
COPY scripts/ ./stringwave/scripts/
COPY webapp/ ./stringwave/webapp/
COPY logs/ ./stringwave/logs/
COPY stringwave.py ./stringwave/
COPY config/icecast.xml ./stringwave/config/
COPY config/ezstream.xml ./stringwave/config/
COPY src/ ./stringwave/src/
COPY app.py ./stringwave/
COPY start.sh ./stringwave/

RUN touch /stringwave/logs/cogmera.log /stringwave/logs/pipefeeder.log /var/log/icecast2/access.log /var/log/icecast2/error.log
RUN chown -R stringwave:stringwave /stringwave/ /var/log/icecast2/access.log /var/log/icecast2/error.log
RUN gcc /stringwave/src/monitor_port.c -o /bin/monitor_port

ENTRYPOINT ["sh", "/stringwave/start.sh"]
