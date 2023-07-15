from subprocess import check_output, STDOUT
import subprocess
import sys
from time import sleep

station = sys.argv[1]

def grab_now_playing(station):
	shell_command = f'tmux capture-pane -t ezstream-{station} -p'
	output = check_output(shell_command, shell=True, stderr=STDOUT, universal_newlines=True).rstrip('\n')
	output = output.split('\n')

	targets = []
	for line in reversed(output):
		# ignore playlist reread and skip notification
		if 'USR1 signal received' in line or 'HUP signal received' in line or 'rereading playlist' in line:
			continue
		elif 'streaming: ' in line and ('(./' in line or '(/s' in line):
			targets.append(line)
			break
		elif 'streaming: ' in line and ('(./' not in line or '(/s' in line):
			targets.append(line)
		elif 'streaming: ' not in line and ('(./' in line or '(/s' in line):
			targets.append(line)
			break

	if len(targets) > 1:
		target = ''.join(targets)
	else:
		target = targets[0]

	if '(./' in target:
		target = target.split('streaming: ')[1].split('(./')[0]
	elif '(/s' in target:
		target = target.split('streaming: ')[1].split('(/s')[0]

	subprocess.run(['clear'])
	print(f'Now playing: {target}')
	with open('/stringwave/webapp/static/now_playing', 'w') as f:
		f.write(target)


if __name__ == '__main__':
	while True:
		grab_now_playing(station)
		sleep(5)

		
