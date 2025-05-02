from subprocess import check_output, STDOUT
import sys
import re

# this is needed to make the queue order work when manually queueing tracks
# see scripts/ezstream-queue.sh for more information
def return_now_playing_file_path(station: str):
	shell_command = f'tmux capture-pane -t ezstream-{station} -p'
	output = check_output(shell_command, shell=True, stderr=STDOUT, universal_newlines=True).rstrip('\n')
	output = output.split('\n')
	regex = r'\s*\[\s+\d+\/\d+\s+]\s{2}\[\s+\d+h\d+m\d+s\/\d+h\d+m\d+s]\s{2}\[\s+\d+\.\d+\s\Dbps]'
	targets = []
	for line in reversed(output):
		if 'too many errors; giving up' in line:
			print("No tracks in playlist")
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
		if 'streaming: ' in line and ('.opus)' in line):
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
			target = target.split('(./')[1].split('.opus)')[0]
		except IndexError:
			pass
	print(f"./{target}.opus")

if __name__ == "__main__":
	station = sys.argv[1]
	return_now_playing_file_path(station)