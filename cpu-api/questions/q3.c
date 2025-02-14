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
        sleep(2);
        printf("[child] hello\n");
    } else {
        // wait(NULL);
        sleep(1);
        printf("[parent] goodbye\n");
    }
}