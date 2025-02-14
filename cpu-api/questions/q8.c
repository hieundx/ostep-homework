#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h> // Include for waitpid

int main() {
    int pipefd[2];

    if (pipe(pipefd) == -1) {
        perror("pipe");
        exit(EXIT_FAILURE);
    }

    int child1 = fork();

    if (child1 < 0) {
        perror("Unable to fork child1.");
        return 1;
    } else if (child1 == 0) {
        // Child 1:  Write to the pipe

        // Close the read end in child1 - it doesn't need it.
        // close(pipefd[0]);

        char message[] = "hello from child 1";
        ssize_t bytes_written = write(pipefd[1], message, sizeof(message));
        if (bytes_written == -1) {
            perror("child1 write");
            exit(EXIT_FAILURE); // Exit on write failure
        }
        close(pipefd[1]); // Close write end after writing
        exit(EXIT_SUCCESS); // Important: Exit the child process
    } else {
        // Parent Process

        //Close the write end, parent only reads
        // close(pipefd[1]);

        int child2 = fork();

        if (child2 < 0) {
            perror("Unable to fork child2.");
            return 1;
        } else if (child2 == 0) {
            // Child 2: Read from the pipe
            // Close the write end in child2 - it doesn't need it.
            // close(pipefd[1]); // Correctly close the unused write end

            char buffer[100];
            ssize_t bytes_read = read(pipefd[0], buffer, sizeof(buffer));
             if (bytes_read == -1) {
                perror("child2 read");
                exit(EXIT_FAILURE);
             }
            buffer[bytes_read] = '\0';  //VERY IMPORTANT: Null-terminate after reading

            printf("Received: %s\n", buffer);
            close(pipefd[0]); // Close read end after reading
            exit(EXIT_SUCCESS); // Exit the child process
        }
        //wait for child1
        // waitpid(child1, NULL, 0);
        //Wait for child 2 to avoid a zombie process
        // waitpid(child2, NULL, 0);
        // close(pipefd[0]); // close the read end of the pipe in the parent
    }

    return 0;
}