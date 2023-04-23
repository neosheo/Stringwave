#include <stdio.h>
#include <stdlib.h>
#include <netdb.h>
#include <unistd.h>

#define handle_error(msg) \
	do { perror(msg); exit(EXIT_FAILURE); } while (0)


void getTrack(int* sock) {
	// prepare socket
	int new_sock;
	int option = 1;
	setsockopt(new_sock, SOL_SOCKET, SO_REUSEADDR, &option, sizeof(option));

	// accept connections
	struct sockaddr_in cli_addr;
	int cli_len = sizeof(cli_addr);
	if ((new_sock = accept(*sock, (struct sockaddr *)&cli_addr, (socklen_t *)&cli_len)) < 0) {
		handle_error("ERROR on accept");
	}

	// receive data and save to disk
	char song_title[200];
	int data_len = recv(new_sock, song_title, 200, 0);
	song_title[data_len] = '\0';

	FILE* fptr;
	char now_playing[] = "/home/john/radio/now_playing";
	fptr = fopen(now_playing, "w");
	if (fptr == NULL) {
                puts("Cannot open file.");
                exit(1);
        }
	fputs(song_title, fptr);
	printf("%s\n", song_title);
	fclose(fptr);

	close(new_sock);
}


void main() {
	// prepare socket
	int sock;
	int option = 1;
	sock = socket(AF_INET, SOCK_STREAM, 0);
	setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &option, sizeof(option));
	if (sock == -1) {
		handle_error("socket");
	}

	// bind socket
	struct sockaddr_in srv_addr;
	srv_addr.sin_family = AF_INET;
	srv_addr.sin_addr.s_addr = INADDR_ANY;
	srv_addr.sin_port = htons(5799);

	if (bind(sock, (struct sockaddr *)&srv_addr, sizeof(srv_addr)) < 0)
		handle_error("ERROR on binding");

	// listen on socket
	if (listen(sock, 5) != 0)
		handle_error("ERROR on listening");

	while (1) {
		getTrack(&sock);
		sleep(5);

	}
}
