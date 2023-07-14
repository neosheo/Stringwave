from subprocess import check_output, STDOUT
import sys
from time import sleep

station = sys.argv[1]

def grab_now_playing(station):
	shell_command = f"tmux capture-pane -t ezstream-{station} -p"
	output = check_output(shell_command, shell=True, stderr=STDOUT, universal_newlines=True).rstrip('\n')
	output = output.split('\n')

	targets = []
	for line in reversed(output):
		if 'streaming: ' in line and '(./' in line:
			targets.append(line)
			break
		elif 'streaming: ' in line and '(./' not in line:
			targets.append(line)
			break
		elif 'streaming: ' not in line and '(./' in line:
			targets.append(line)

	if len(targets) > 1:
		target = ''.join(targets)
	else:
		target = targets[0]

	target = target.split('streaming: ')[1].split('(./')[0]

	print(target)
	with open('/stringwave/webapp/static/now_playing', 'w') as f:
		f.write(target)


if __name__ == '__main__':
	while True:
		grab_now_playing(station)
		sleep(5)

		
