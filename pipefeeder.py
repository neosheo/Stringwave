import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from webapp import pf_logger as logger
from tqdm import tqdm
import sqlite3
import time
import subprocess
import os

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
		logger.debug(f"Channel ID found: {chan_id}")
	# get the rss feed for the channel
	feed_url = f"https://youtube.com/feeds/videos.xml?channel_id={chan_id}"
	logger.debug(f"BUILT FEED URL: {feed_url}")
	feed = requests.get(feed_url).text
	return feed


def get_channel_url(feed):
	return BeautifulSoup(feed, "xml").find("uri").text


def get_channel_name(feed):
	return BeautifulSoup(feed, "xml").find("title").text


def get_channel_id(feed):
	return BeautifulSoup(feed, "xml").find_all("yt:channelId")[1].text


def get_channel_icon(channel_url):
	logger.debug(f"GETTING ICON FOR {channel_url}")
	channel_html = requests.get(channel_url).text
	soup = BeautifulSoup(channel_html, "html.parser")
	links = soup.find_all("link")
	for link in links:
		if link["rel"][0] == "image_src":
			logger.debug(f"{link['rel']} IS AN ICON FOR {channel_url}")
			icon = requests.get(link["href"]).content
			channel_id = channel_url.split("/")[-1]
			icon_uri = f"/stringwave/webapp/static/images/channel_icons/{channel_id}.jpg"
			with open(icon_uri, "wb") as f:
				f.write(icon)
			logger.debug(f"SAVED CHANNEL ICON TO {icon_uri}")
			return
		else:
			logger.debug(f"{link['rel']} IS NOT AN ICON FOR {channel_url}")
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
	# pull channel id from feed instead of parsing from xml because sometimes videos from other channels are included
	# mostly on artists with a vevo channel, videos may be listed with the vevo channel id that isn't in the database
	# channel_id = feed.split("channel_id=")[1]
	# channel_id = feed_soup.find_all("yt:channelId")[1].text.strip() 
	channel_id = feed_soup.find("link")["href"].split("channel_id=")[1].strip()
	logger.debug(f"EXTRACTED CHANNEL ID FROM FEED URL: {channel_id}")
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
			logger.debug(f"NEW VIDEO FOUND: {videos[index].text}")
			logger.debug(f"NEW VIDEO LINK: {titles[index].text}")
		index += 1
	# extract video urls
	urls = [ new_video[0].attrs["url"].split("?")[0].rstrip() for new_video in new_videos ]
	titles = [ new_video[1].text for new_video in new_videos ]
	for i, url in enumerate(urls):
		tqdm.write(f"Link found: {url} by {channel}")
		with open("dl_data/urls", "a") as f:
			f.write(f"{url};{channel_id};{titles[i]};\n")


def build_playlist():
	# clear old urls
	open("dl_data/urls", "w").close()
	# retrieve channel urls from database
	con = sqlite3.connect("webapp/instance/stringwave.db")
	subscriptions = [
		f"https://youtube.com/channel/{chan_id[0]}" for chan_id in con.cursor().execute("SELECT channel_id FROM subs").fetchall()
		
	]
	print("Fetching new video URLs...", flush=True)
	for subscription in tqdm(subscriptions):
		try:
			logger.debug(f"DOWNLOADING FEED FOR {subscription}")
			feed = get_channel_feed(subscription)
			get_recent_uploads(feed)
		except requests.exceptions.ConnectionError:
			logger.error(f"Connection error for {subscription}")
			continue
	with open("dl_data/urls", "r") as f:
		num_urls = len(f.readlines())
		logger.debug(f"FOUND {num_urls} LINKS")
	print(f"Grabbed {num_urls} URLs!", flush=True)
	requests.get("http://gateway:8080/download/pipefeeder")


def populate_database(text_file):
	with open(text_file, "r") as f:
		channel_ids = f.readlines()
	subscriptions = []
	print("Gathering subscriptions...", flush=True)
	for channel_id in tqdm(channel_ids):
		logger.debug(f"EXTRACTING CHANNEL DATA FOR ID: {channel_id}")
		try:
			channel_id = channel_id.strip()
			channel_url = f"https://youtube.com/channel/{channel_id}"
			feed = get_channel_feed(channel_url)
			logger.debug(f"GOT FEED FOR {channel_url}")
			# channel_id = get_channel_id(feed)
			channel_name = get_channel_name(feed)
			logger.debug(f"CHANNEL NAME IS {channel_name}")
			# get_channel_icon(get_channel_url(feed))
			get_channel_icon(channel_url)
			subscriptions.append((channel_id, channel_name))
			time.sleep(3)
		except requests.exceptions.ConnectionError:
			time.sleep(3)
			continue
	print("Done!", flush=True)
	print("Updating database...", flush=True)
	con = sqlite3.connect("webapp/instance/stringwave.db")
	cur = con.cursor()
	cur.executemany(
		"INSERT OR IGNORE INTO subs(channel_id, channel_name) VALUES (?, ?)",
		subscriptions,
	)
	con.commit()
	print("Done!", flush=True)


if __name__ == "__main__":
	build_playlist()
	while True:
		status_file = "dl_data/pf_download_status"
		# create download status file if it doesn't exist
		if not os.path.isfile(status_file):
			open(status_file, "w").close()

		with open(status_file, "r") as f:
			if f.read() == "Done":
				requests.get("http://gateway:8080/reread")
				logger.debug("RECEIVED NOTICE THAT ALL DOWNLOADS ARE COMPLETE")
				break
			time.sleep(5)
	open(status_file, "w").close()
	# remove any duplicate database entries and illegal filenames
	print("Cleaning up...", flush=True)
	res = subprocess.run(["./scripts/cleanup.sh"])
	print("Done!", flush=True)
	logger.debug(f"CLEANUP SCRIPT EXIT CODE: {res.returncode}")
	print("Done!", flush=True)
