#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

int main(int argc, char* argv[]) {
    char * var;

    if (argc <= 1) {
        var = "execvp";
    } else {
        var = argv[1];
    }

    printf("Variant: %s\n", var);

    int rc = fork();

    if (rc == 0) {
   
        if (strcmp(var, "execl") == 0) { // provide path
            execl("/bin/ls", "ls", "-l", NULL);
        }
        
        if (strcmp(var, "execle") == 0) {
            char *const envp[] = {"FILE_NAME=data.txt", NULL};
            execle("/usr/bin/env", "env", NULL, envp);
        }

        if (strcmp(var, "execlp") == 0) {
            execlp("ls", "ls", "-l", NULL);
        }

        if (strcmp(var, "execv") == 0) {
            char *const argv[] = {"ls", "-l", NULL};
            execv("/bin/ls", argv);
        }

        if (strcmp(var, "execvp") == 0) { // auto resolve path
            char *const argv[] = {"ls", "-l", NULL};
            execvp("ls", argv);
        }

        if (strcmp(var, "execvpe") == 0) { // auto resolve path
            char *const envp[] = {"FILE_NAME=data.txt", NULL};
            char *const argv[] = {"env", NULL};
            execvpe("env", argv, envp);
        }

        perror("Error");
        return 1;
    } else if (rc > 0) {
        // do nothing.
    } else {
        perror("Failed to fork.");
        return 1;
    }

    return 0;
}