FROM python:3.11.3-slim-bullseye

WORKDIR /cogmera

RUN apt-get update && apt-get upgrade -y
RUN apt-get install gcc cron -y

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN rm requirements.txt

RUN groupadd -r --gid 1000 cogmera && useradd -r --uid 1000 -g cogmera cogmera
RUN chsh --shell /usr/sbin/nologin root

COPY app.py .
COPY cogmera.py .
COPY webapp/ ./webapp/
COPY start.sh .
COPY run.py .
COPY run.sh .

RUN touch /cogmera/webapp/instance/configs.db
RUN chown -R cogmera:cogmera /cogmera/
RUN echo "0 3 * * * ./run.sh" | crontab -u cogmera -

ENTRYPOINT [ "bash", "./start.sh" ]
