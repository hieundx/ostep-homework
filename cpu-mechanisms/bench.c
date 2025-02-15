#include <sys/time.h>
#include <time.h>
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

long timestamp_ms() {
    struct timeval tv;
    time_t curtime;

    gettimeofday(&tv, NULL);
    curtime = tv.tv_sec * 1000000 + tv.tv_usec;

    return curtime;
}

int main() {
    long time_s = timestamp_ms();
    int fd = open("example.txt", O_RDONLY);
    long time_e = timestamp_ms();
    printf("open() took: %ld (ms)\n", time_e - time_s);

    time_s = timestamp_ms();
    char buffer[10];
    ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);
    time_e = timestamp_ms();
    printf("read() took: %ld (ms)\n", time_e - time_s);

    time_s = timestamp_ms();
    close(fd);
    time_e = timestamp_ms();
    printf("close() took: %ld (ms)\n", time_e - time_s);
}