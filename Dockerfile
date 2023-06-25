FROM python:3.11.3-slim-bullseye

WORKDIR /stringwave

RUN apt-get update && apt-get upgrade -y 
RUN apt-get install ffmpeg icecast2 ezstream gcc tmux procps sqlite3 curl -y
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN rm requirements.txt

RUN groupadd -r --gid 1000 stringwave && useradd -r --uid 1000 -g stringwave stringwave
RUN chsh --shell /usr/sbin/nologin root

COPY radio/ ./radio/
COPY scripts/ ./scripts/
COPY webapp/ ./webapp/
COPY config/ ./config/
COPY src/ ./src/
COPY app.py .
COPY start.sh .
COPY tasks.py .

RUN mkdir urls logs /home/stringwave
RUN touch logs/cogmera_download.log logs/cogmera_selection.log logs/pipefeeder.log /var/log/icecast2/access.log /var/log/icecast2/error.log webapp/static/move_status urls/urls .completed_downloads
RUN echo 99999 > .pid-new
RUN echo 99999 > .pid-main
RUN export NUM_DAILY_DOWNLOADS=$NUM_DAILY_DOWNLOADS
RUN echo 0 > .completed_downloads_cogmera
RUN echo 0 > .completed_downloads_pipefeeder
RUN chown -R stringwave:stringwave /stringwave/ /var/log/icecast2/access.log /var/log/icecast2/error.log /home/stringwave
RUN gcc src/monitor_port.c -o /bin/monitor_port

ENTRYPOINT ["bash", "./start.sh"]
