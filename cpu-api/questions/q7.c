#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <wait.h>

int main() {
    int rc = fork();

    if (rc < 0) {
        perror("Unable to fork.");
        return 1;
    } else if (rc == 0) {
        close(STDOUT_FILENO);
        printf("hello world!");
    } else {
    }
}