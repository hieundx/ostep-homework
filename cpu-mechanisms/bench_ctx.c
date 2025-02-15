#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/time.h>

#define NUM_ITERATIONS 100000 // Number of context switches to measure
#define PIPE_READ 1
#define PIPE_WRITE 1
#define BUF_SIZE 100

long timestamp_ms() {
    struct timeval tv;
    time_t curtime;

    gettimeofday(&tv, NULL);
    curtime = tv.tv_sec * 1000000 + tv.tv_usec;

    return curtime;
}


int main()
{
    int pipe1[2]; // Pipe from parent to child (Process 1 to Process 2)
    int pipe2[2]; // Pipe from child to parent (Process 2 to Process 1)
    char buf[BUF_SIZE];
    int NUM_ITER = 100000;
    
    int rc = fork();

    if (rc == 0) {
        close(pipe1[PIPE_READ]);
        close(pipe2[PIPE_WRITE]);

        for (int i = 0; i < NUM_ITER; i++) {
            // write to pipe1
            const char *msg_child = "hello from child!";
            write(pipe1[PIPE_WRITE], msg_child, strlen(msg_child));

            // read from pipe 2
            read(pipe2[PIPE_READ], buf, BUF_SIZE);
        }

        close(pipe1[PIPE_WRITE]);
        close(pipe2[PIPE_READ]);
    } else {
        close(pipe1[PIPE_READ]);
        close(pipe2[PIPE_WRITE]);

        double elasped = 0;
        for (int i = 0; i < NUM_ITER; i++) {
            long time_s = timestamp_ms();

            read(pipe1[PIPE_READ], buf, BUF_SIZE);

            const char *msg_parent = "hello from parent!";
            write(pipe2[PIPE_WRITE], msg_parent, strlen(msg_parent));

            long time_e = timestamp_ms();
            elasped = elasped + (time_e - time_s);
        }

        printf("Took %.2f (ms) on average\n", (double) (elasped) / (double) NUM_ITER);

        close(pipe1[PIPE_WRITE]);
        close(pipe2[PIPE_READ]);
    }

    return EXIT_SUCCESS;
}