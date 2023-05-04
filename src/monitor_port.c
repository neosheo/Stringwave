#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>

void respond_to_ping(int* sockfd) {
	int new_sockfd;
	int option = 1;
	setsockopt(new_sockfd, SOL_SOCKET, SO_REUSEADDR, &option, sizeof(option));
	if (new_sockfd == -1)
		puts("Error creating second socket.");

	// accept connections
        struct sockaddr* peer_addr;
        int addr_len = sizeof(peer_addr);
        if ((new_sockfd = accept(*sockfd, peer_addr, (socklen_t *)&addr_len)) < 0)
		puts("Error accepting conection.");
}


void main() {
	// create socket
	int sockfd = socket(AF_INET, SOCK_STREAM, 0);
	int option = 1;
	setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &option, sizeof(option));
	if (sockfd == -1)
		puts("Error creating socket.");

	// bind socket
	struct sockaddr_in addr;
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = inet_addr("0.0.0.0");
	addr.sin_port = htons(5800);
	if (bind(sockfd, (struct sockaddr*)&addr, sizeof(addr)) < 0)
		puts("Error binding socket.");

	// listen on socket
	if (listen(sockfd, 5) == -1)
		puts("Error listening.");

	while (1) {
		respond_to_ping(&sockfd);	
	}
}
