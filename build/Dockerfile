FROM python:3.12.4-slim-bullseye

WORKDIR /stringwave

RUN apt-get update && apt-get upgrade -y 
RUN apt-get install ezstream gcc tmux procps sqlite3 python3-lxml -y

COPY build/requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

RUN groupadd -r --gid 1000 stringwave && useradd -r --uid 1000 -g stringwave stringwave
RUN chsh --shell /usr/sbin/nologin root

COPY radio/ ./radio/
COPY scripts/ ./scripts/
COPY logs/ ./logs/
COPY webapp/ ./webapp/
COPY config/ezstream-*.xml ./config/
# COPY src/ ./src/
COPY app.py .
COPY cogmera.py .
COPY pipefeeder.py .
COPY disallowed_titles.py .
COPY start.sh .
COPY tasks.py .
COPY run.sh .

RUN mkdir /home/stringwave
# RUN [ -f webapp/instance/stringwave.db ] || touch webapp/instance/stringwave.db
RUN echo 99999 > .pid-new
RUN echo 99999 > .pid-main
RUN chown -R stringwave:stringwave \
    /stringwave/ \
    /home/stringwave
# RUN gcc src/monitor_port.c -o /bin/monitor_port

USER stringwave
ENTRYPOINT ["bash", "./start.sh"]
