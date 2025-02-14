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
        printf("[child] %d\n", getpid());
    } else {
        pid_t wait_rs = wait(&rc);
        printf("Wait: %d\n", (int) wait_rs);
        printf("[parent] %d\n", getpid());
        printf("[parent] done\n");
    }
}