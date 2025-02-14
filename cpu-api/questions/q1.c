#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void main() {
    int x = 100;

    printf("Before fork: x = %d\n", x);
    printf("\n");

    int rc = fork();

    if (rc < 0) {
        printf("Fork failed\n");
        exit(1);
    } else if (rc == 0) {
        printf("Child (pid:%d)\n", (int) getpid());
        printf("x = %d\n", x); // 100
        x = 101;
        printf("x changed to %d\n", x); // 101
        printf("\n");
    } else {
        printf("Parent (pid:%d)\n", (int) getpid());
        printf("x = %d\n", x); // 100
        x = 102;
        printf("x changed to %d\n", x); // 102
        printf("\n");
    }
}