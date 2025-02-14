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
        pid_t wait_rs = wait(NULL);
        printf("Wait: %d\n", (int) wait_rs);
        printf("[child] %d\n", getpid());
    } else {
        printf("[parent] %d\n", getpid());
        sleep(3);
        printf("[parent] done\n");
    }
}