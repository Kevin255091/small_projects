#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* concat(const char *s1, const char *s2, const char *glue)
{
    char *result = malloc(strlen(s1) + strlen(s2) + strlen(glue) + 1); // +1 for the null-terminator
    // in real code you would check for errors in malloc here
    strcpy(result, s1);
    strcat(result, glue);
    strcat(result, s2);
    return result;
}

int main(int argc, char *argv[])
{
    char *command = "python C:\\Users\\KevinLin\\PythonCode\\mydir.py";
    if (argc == 1) {
        system(command);
        return 0;
    }

    if (argc > 1) {
        int i = 0;
        for (i = 1; i < argc; i++)
        {
            command = concat(command, argv[i], " ");
        }
        system(command);
    }

    return 0;
}
