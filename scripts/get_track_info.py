import subprocess
from time import sleep
from os.path import exists

with open('.pid', 'r') as f:
	pid = f.read().strip()

def getCurrentTrack():
	output = subprocess.run(['journalctl', f'_PID={pid}', '-n 1', '--no-pager'], stdout=subprocess.PIPE)
	try:
		now_playing = output.stdout.decode().split('streaming: ')[1].split(' (/stringwave/')[0]
		if exists('now_playing'):
			with open('now_playing', 'w') as f:
				f.write(now_playing)
		print(now_playing)
	except IndexError:
		pass


if __name__ == '__main__':
	while True:
		getCurrentTrack()
		subprocess.run(['/stringwave/bin/sender'])
		sleep(5)
