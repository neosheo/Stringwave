#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>


int main() {
	// create socket
	int sock = socket(AF_INET, SOCK_STREAM, 0);
	if (sock == -1) {
		puts("couldn't create socket");
		exit(1);
	}

	// input connection information
	struct sockaddr_in web_server;
	web_server.sin_family = AF_INET;
	web_server.sin_addr.s_addr = inet_addr("10.64.187.7");
	web_server.sin_port = htons(5799);

	// connect
	int conn = connect(sock, (struct sockaddr *)&web_server, sizeof(web_server));
	if (conn < 0) {
		puts("Couldn't connect to socket");
		exit(1);
	}
	//puts("Connection successful!");

	// read metadata from now_playing
	FILE *fptr;
	char filename[] = "/home/$USER/Music/Radio/now_playing";
	char c;

	fptr = fopen(filename, "r");
	if (fptr == NULL) {
		puts("Cannot open file.");
		exit(1);
	}
	
	// write metadata to file
	char *song_title = malloc(200);
	int len = 0;
	c = fgetc(fptr);
	while (c != EOF) {
		song_title[len] = c;
		c = fgetc(fptr);
		len++;
	}
	song_title[len] = '\0';
	len++;
	fclose(fptr);
	send(sock, song_title, len, 0); 
	free(song_title);

	return 0;
}

