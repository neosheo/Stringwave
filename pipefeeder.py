import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from tqdm import tqdm
import sqlite3
import time
import re
import subprocess


def get_channel_feed(channel=None):
    # get the html of the requested youtube channel
    if channel:
        chan_url = channel.rstrip()
    else:
        chan_url = input("Enter a youtube channel link: ")
    # find the channel id
    if "/channel/" in chan_url:
        chan_id = chan_url.split("/")[-1].rstrip()
    elif "/c/" in chan_url:
        chan_html = requests.get(chan_url).text
        browse_id_index = chan_html.find("browse_id")
        id_start = browse_id_index + 20
        id_end = browse_id_index + 44
        chan_id = chan_html[id_start:id_end]
    elif "@" in chan_url:
        chan_html = requests.get(chan_url).text
        chan_soup = BeautifulSoup(chan_html, "html.parser")
        alt_chan_url = chan_soup.find("link", rel="canonical")["href"]
        chan_id = alt_chan_url.split("/")[-1].rstrip()
    # get the rss feed for the channel
    feed_url = f"https://youtube.com/feeds/videos.xml?channel_id={chan_id}"
    feed = requests.get(feed_url).text
    # print(feed)
    return feed


def get_channel_url(feed):
    return BeautifulSoup(feed, "xml").find("uri").text


def get_channel_name(feed):
    return BeautifulSoup(feed, "xml").find("title").text


def get_channel_id(feed):
    return BeautifulSoup(feed, "xml").find_all("yt:channelId")[1].text


def get_channel_icon(channel_url):
    channel_html = requests.get(channel_url).text
    soup = BeautifulSoup(channel_html, "html.parser")
    links = soup.find_all("link")
    for link in links:
        if link["rel"][0] == "image_src":
            return link["href"]
        else:
            continue


def get_recent_uploads(feed):
    now = datetime.now()
    period = timedelta(days=1)
    feed_soup = BeautifulSoup(feed, "xml")
    # parse the video urls and  dates published
    # remove first date entry which is the channel published date
    pub_dates = feed_soup.find_all("published")[1:]
    videos = feed_soup.find_all("media:content")
    channel = feed_soup.find("title").text.rstrip()
    titles = feed_soup.find_all("media:title")
    # check if videos are were published before your specified period
    # if they are within your specified period, include them
    index = 0
    new_videos = []
    for pub_date in pub_dates:
        if period < now - datetime.strptime(
            pub_date.text.replace("T", " ").split("+")[0], "%Y-%m-%d %H:%M:%S"
        ):
            continue
        else:
            new_videos.append((videos[index], titles[index]))
        index += 1
    # extract video urls
    urls = [ new_video[0].attrs["url"].split("?")[0].rstrip() for new_video in new_videos ]
    titles = [ new_video[1].text for new_video in new_videos ]
    for i, url in enumerate(urls):
        tqdm.write(f"Link found: {url} by {channel}")
        with open("dl_data/urls", "a") as f:
            f.write(f"{url};{channel};{titles[i]}\n")


def build_playlist():
    open("dl_data/urls", "w").close()
    con = sqlite3.connect("webapp/instance/stringwave.db")
    subscriptions = [
        x[0] for x in con.cursor().execute("SELECT channel_url FROM subs").fetchall()
    ]
    print("Fetching new video URLs...", flush=True)
    for subscription in tqdm(subscriptions):
        try:
            feed = get_channel_feed(subscription)
            get_recent_uploads(feed)
        except requests.exceptions.ConnectionError:
            tqdm.write(f"Connection error for {subscription}")
            continue
    with open("dl_data/urls", "r") as f:
        num_urls = len(f.readlines())
    print(f"Grabbed {num_urls} URLs!", flush=True)
    requests.get("http://gateway:8080/download/pipefeeder")


def populate_database(text_file):
    with open(text_file, "r") as f:
        subs = f.readlines()
    subscriptions = []
    print("Gathering subscriptions...", flush=True)
    for sub in tqdm(subs):
        try:
            feed = get_channel_feed(sub)
            channel_id = get_channel_id(feed)
            channel_name = get_channel_name(feed)
            channel_url = get_channel_url(feed)
            channel_icon = get_channel_icon(channel_url)
            subscriptions.append((channel_id, channel_name, channel_url, channel_icon))
            time.sleep(3)
        except requests.exceptions.ConnectionError:
            time.sleep(3)
            continue
    print("Done!", flush=True)
    print("Updating database...", flush=True)
    con = sqlite3.connect("webapp/instance/stringwave.db")
    cur = con.cursor()
    cur.executemany(
        "INSERT OR IGNORE INTO subs(channel_id, channel_name, channel_url, channel_icon) VALUES (?, ?, ?, ?)",
        subscriptions,
    )
    con.commit()
    print("Done!", flush=True)


if __name__ == "__main__":
    build_playlist()
    while True:
        with open("dl_data/pf_download_status", "r") as f:
            if f.read() == "Done":
                requests.get("http://gateway:8080/reread")
                break
            time.sleep(5)
    subprocess.run(["sed", "-i", "/stringwave/d", "logs/pipefeeder.log"])
    open("dl_data/pf_download_status", "w").close()
    print("Done!", flush=True)
