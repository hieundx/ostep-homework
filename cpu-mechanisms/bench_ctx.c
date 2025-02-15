#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <string.h>
#include <sys/wait.h>

#define NUM_ITERATIONS 100000 // Number of context switches to measure
#define MESSAGE "go"
#define MESSAGE_SIZE sizeof(MESSAGE)

int main()
{
    int pipe1[2]; // Pipe from parent to child (Process 1 to Process 2)
    int pipe2[2]; // Pipe from child to parent (Process 2 to Process 1)
    pid_t child_pid;
    struct timespec start_time, end_time;
    long long total_time = 0;
    int i;
    char buffer[MESSAGE_SIZE];

    if (pipe(pipe1) == -1 || pipe(pipe2) == -1)
    {
        perror("Pipe creation failed");
        return EXIT_FAILURE;
    }

    child_pid = fork();
    if (child_pid == -1)
    {
        perror("Fork failed");
        close(pipe1[0]);
        close(pipe1[1]);
        close(pipe2[0]);
        close(pipe2[1]);
        return EXIT_FAILURE;
    }

    if (child_pid == 0)
    { // Child process (Process 2)
        // Close unused pipe ends
        close(pipe1[1]); // Close write end of pipe1 (parent -> child write)
        close(pipe2[0]); // Close read end of pipe2 (child -> parent read)

        for (i = 0; i < NUM_ITERATIONS; ++i)
        {
            // Wait for message from parent (blocking read)
            if (read(pipe1[0], buffer, MESSAGE_SIZE) == -1)
            {
                perror("Child read from pipe1 failed");
                exit(EXIT_FAILURE);
            }

            // Send message back to parent
            if (write(pipe2[1], MESSAGE, MESSAGE_SIZE) == -1)
            {
                perror("Child write to pipe2 failed");
                exit(EXIT_FAILURE);
            }
        }

        close(pipe1[0]);
        close(pipe2[1]);
        exit(EXIT_SUCCESS);
    }
    else
    { // Parent process (Process 1)
        // Close unused pipe ends
        close(pipe1[0]); // Close read end of pipe1 (parent -> child read)
        close(pipe2[1]); // Close write end of pipe2 (child -> parent write)

        for (i = 0; i < NUM_ITERATIONS; ++i)
        {
            clock_gettime(CLOCK_MONOTONIC, &start_time);

            // Send message to child to trigger context switch
            if (write(pipe1[1], MESSAGE, MESSAGE_SIZE) == -1)
            {
                perror("Parent write to pipe1 failed");
                close(pipe1[1]);
                close(pipe2[0]);
                wait(NULL); // Clean up child process
                return EXIT_FAILURE;
            }

            // Wait for message back from child (blocking read)
            if (read(pipe2[0], buffer, MESSAGE_SIZE) == -1)
            {
                perror("Parent read from pipe2 failed");
                close(pipe1[1]);
                close(pipe2[0]);
                wait(NULL); // Clean up child process
                return EXIT_FAILURE;
            }

            clock_gettime(CLOCK_MONOTONIC, &end_time);

            // Calculate elapsed time in nanoseconds
            long long elapsed_ns = (end_time.tv_sec - start_time.tv_sec) * 1000000000LL + (end_time.tv_nsec - start_time.tv_nsec);
            total_time += elapsed_ns;
        }

        double avg_time_ns = (double)total_time / NUM_ITERATIONS;
        double avg_time_us = avg_time_ns / 1000.0;

        printf("Average context switch time over %d iterations:\n", NUM_ITERATIONS);
        printf("Average time: %.2f nanoseconds (%.2f microseconds)\n", avg_time_ns, avg_time_us);

        close(pipe1[1]);
        close(pipe2[0]);
        wait(NULL); // Wait for child process to exit
    }

    return EXIT_SUCCESS;
}