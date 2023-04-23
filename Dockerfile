FROM python:3.11.3-slim-bullseye

# RUN \
#     --mount=type=cache,target=/var/cache/apt \
RUN apt-get update && apt-get upgrade -y && \
    apt-get install ffmpeg icecast2 ezstream openssh-server gcc tmux -y
COPY requirements.txt .
RUN python -m pip install --upgrade pip
# RUN \
#     --mount=type=cache,target=/pip-packages \
RUN python -m pip install -r requirements.txt 
#--target=/pip-packages
RUN groupadd -r dj && useradd -r -g dj dj
RUN chsh --shell /sbin/nologin root

COPY radio/ ./stringwave/radio/
COPY scripts/ ./stringwave/scripts/
COPY webapp/ ./stringwave/webapp/
COPY stringwave.py ./stringwave
COPY config/sshd_config /etc/ssh/
COPY config/icecast.xml ./stringwave/config/
COPY config/ezstream.xml ./stringwave/config/
COPY src/ ./stringwave/src
COPY app.py ./stringwave/
COPY start.sh ./stringwave/

RUN gcc /stringwave/src/monitor_port.c -o /bin/monitor_port

ENTRYPOINT ["sh", "/stringwave/start.sh"]
