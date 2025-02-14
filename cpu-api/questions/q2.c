#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <string.h>

#define BUFFER_SIZE 256

int read_fd(int fd, char* prefix) {
    lseek(fd, 0, SEEK_SET);

    char buffer[BUFFER_SIZE];
    ssize_t bytes_read;

    printf("%s ", prefix);
    while((bytes_read = read(fd, buffer, sizeof(buffer))) > 0) {
        buffer[bytes_read] = '\0';
        printf("%s", buffer);
    }

    if (bytes_read == -1) {
        perror("Error reading file");
        close(fd);
        return 1;
    }
    return 0;
}

int write_fd(int fd, char* str) {
    size_t str_len = strlen(str);

    if(write(fd, str, str_len) != str_len) {
        perror("Error writing to file.\n");
        close(fd);
        return 1;
    }
}

int main() {
    int fd = open("data.txt", O_RDWR, 0644);
    if (fd == -1) {
        perror("Error opening file.");
        return -1;
    }
    int rc = fork();

    if (rc < 0) {
        printf("Fork failed\n");
        exit(1);
    } else if (rc == 0) {
        printf("[child] read_start\n");
        read_fd(fd, "[child]");
        printf("[child] read_end\n");
        printf("[child] write_start\n");
        write_fd(fd, "child\n");
        printf("[child] write_end\n");
    } else {
        printf("[parent] read_start\n");
        read_fd(fd, "[parent]");
        printf("[parent] read_end\n");
        printf("[parent] write_start\n");
        write_fd(fd, "parent\n");
        printf("[parent] write_end\n");
    }
}