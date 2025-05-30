from subprocess import check_output, STDOUT
import subprocess
import sys
from time import sleep
import re

# write_to_file is needed to add currently playing track to the front of the queue
# when queueing a track this is necessary to make the queued track play next
def grab_now_playing(station, write_to_file):
	shell_command = f'tmux capture-pane -t ezstream-{station} -p'
	output = check_output(shell_command, shell=True, stderr=STDOUT, universal_newlines=True).rstrip('\n')
	output = output.split('\n')
	regex = r'\s*\[\s+\d+\/\d+\s+]\s{2}\[\s+\d+h\d+m\d+s\/\d+h\d+m\d+s]\s{2}\[\s+\d+\.\d+\s\Dbps]'
	targets = []
	for line in reversed(output):
		if 'too many errors; giving up' in line:
			with open(f'/stringwave/webapp/static/now_playing_{station}', 'w') as f:
				f.write('No more tracks in playlist')
			continue
		# ignore playlist reread and skip notification
		if 'USR1 signal received' in line or 'HUP signal received' in line or 'rereading playlist' in line:
			continue
		# cut any lines with stream info
		if re.match(regex, line):
			continue
		# append all lines together until both beginning and ending strings are found
		if len(targets) > 0:
			targets.append(line)
			line = ''.join(reversed(targets))
		if 'streaming: ' in line and ('(./' in line or '(/s' in line):
			targets.append(line)
			break
		if len(targets) == 0:
			targets.append(line)

	if len(targets) > 1:
		target = ''.join(reversed(targets))
	else:
		try:
			target = targets[0]
		except IndexError:
			pass
	try:
		target
	except NameError:
		return

	if 'ezstream.sh' in target:
		target = 'No tracks found'

	if '(./' in target:
		try:
			target = target.split('streaming: ')[1].split('(./')[0]
		except IndexError:
			pass
	elif '(/s' in target:
		try:
			target = target.split('streaming: ')[1].split('(/s')[0]
		except IndexError:
			pass		
	target = re.sub(r'_+', ' ', target)
	if write_to_file:
		subprocess.run(['clear'])
		print(f'Now playing: {target}')
		with open(f'/stringwave/webapp/static/now_playing_{station}', 'w') as f:
			f.write(target)
	else:
		return target


if __name__ == '__main__':
	station = sys.argv[1]
	write_to_file = sys.argv[2]
	while True:
		grab_now_playing(station, write_to_file)
		sleep(5)	
