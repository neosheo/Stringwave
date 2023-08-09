import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from tqdm import tqdm
import sqlite3
from bad_words import bad_words
import re
import time


def getChannelFeed(channel=None):
	# get the html of the requested youtube channel
	if channel:
		chan_url = channel.rstrip()
	else:
		chan_url = input('Enter a youtube channel link: ')
	# find the channel id
	if '/channel/' in chan_url:
		chan_id = chan_url.split('/')[-1].rstrip()
	elif '/c/' in chan_url:	
		chan_html = requests.get(chan_url).text
		browse_id_index = chan_html.find('browse_id')
		id_start = browse_id_index + 20
		id_end = browse_id_index + 44
		chan_id = chan_html[id_start:id_end]
	elif '@' in chan_url:
		chan_html = requests.get(chan_url).text
		chan_soup = BeautifulSoup(chan_html, 'html.parser')
		alt_chan_url = chan_soup.find('link', rel='canonical')['href']
		chan_id = alt_chan_url.split('/')[-1].rstrip()
	# get the rss feed for the channel
	feed_url = f'https://youtube.com/feeds/videos.xml?channel_id={chan_id}'
	feed = requests.get(feed_url).text
	#print(feed)
	return feed


def getChannelUrl(feed):
	return BeautifulSoup(feed, 'xml').find('uri').text


def getChannelName(feed):
	return BeautifulSoup(feed, 'xml').find('title').text


def getChannelId(feed):
	return BeautifulSoup(feed, 'xml').find_all('yt:channelId')[1].text


def getChannelIcon(channel_url):
	channel_html = requests.get(channel_url).text
	soup = BeautifulSoup(channel_html, 'html.parser')
	links = soup.find_all('link')
	for link in links:
		if link['rel'][0] == 'image_src':
			return link['href']
		else:
			continue
	

def getRecentUploads(feed):
	now = datetime.now()
	period = timedelta(days = 1)
	feed_soup = BeautifulSoup(feed, 'xml')
	# parse the video urls and  dates published
	# remove first date entry which is the channel published date
	pub_dates = feed_soup.find_all('published')[1:]
	videos = feed_soup.find_all('media:content')
	titles = feed_soup.find_all('media:title')
	channel = feed_soup.find('title')
	# remove any videos that contain words in the bad_words.py file
	for i, title in enumerate(titles):
		for bad_word in bad_words:
			if re.match(bad_word, title.text, flags=re.IGNORECASE):
				titles.remove(title)
				del pub_dates[i]
				del videos[i]
	# check if videos are were published before your specified period 
	# if they are within your specified period, include them
	index = 0
	new_videos = []
	for pub_date in pub_dates:
		if period < now - datetime.strptime(pub_date.text.replace('T', ' ').split('+')[0], '%Y-%m-%d %H:%M:%S'):
			continue
		else:
			new_videos.append(videos[index])
		index += 1
	# extract video urls
	urls = [new_video.attrs['url'].split('?')[0] for new_video in new_videos]
	for url in urls:
		with open('dl_data/urls', 'a') as f:
			f.write(f'{url};{channel}\n')


def buildPlaylist():
	open('dl_data/urls', 'w').close()
	con = sqlite3.connect('webapp/instance/stringwave.db')
	subscriptions = [x[0] for x in con.cursor().execute('SELECT channel_url FROM subs').fetchall()]
	print('Fetching new video URLs...')
	for subscription in tqdm(subscriptions):
		try:
			feed = getChannelFeed(subscription)
			getRecentUploads(feed)
			time.sleep(3)
		except requests.exceptions.ConnectionError:
			time.sleep(3)
			continue
	with open('dl_data/urls', 'r') as f:
		num_urls = len(f.readlines())
	print(f'Grabbed {num_urls} URLs!')
	requests.get('http://gateway:8080/download/pipefeeder')
	requests.get('http://gateway:8080/check_download_completion/pipefeeder')


def populateDb(text_file):
	with open(text_file, 'r') as f:
		subs = f.readlines()
	subscriptions = []
	print('Gathering subscriptions...')
	for sub in tqdm(subs):
		try:
			feed = getChannelFeed(sub)
			channel_id = getChannelId(feed)
			channel_name = getChannelName(feed)
			channel_url = getChannelUrl(feed)
			channel_icon = getChannelIcon(channel_url)
			subscriptions.append((channel_id, channel_name, channel_url, channel_icon))
			time.sleep(3)
		except requests.exceptions.ConnectionError:
			time.sleep(3)
			continue	
	print('Done!')
	print('Updating database...')
	con = sqlite3.connect('webapp/instance/stringwave.db')
	cur = con.cursor()
	cur.executemany('INSERT OR IGNORE INTO subs(channel_id, channel_name, channel_url, channel_icon) VALUES (?, ?, ?, ?)', subscriptions)
	con.commit()
	print('Done!')


if __name__ == '__main__':
		buildPlaylist()
		while True:
			with open('dl_data/pf_download_status', 'r') as f:
				if f.read() == 'Done':
					requests.get('http://gateway:8080/reread')
					break
				time.sleep(5)
		open('dl_data/pf_download_status', 'w').close()
