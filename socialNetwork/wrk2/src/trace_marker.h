#ifndef TRACE_MARKER
#define TRACE_MARKER
#define MAX_PATH 256
#define _STR(x) #x
#define STR(x) _STR(x)

#include <stdio.h>
#include <string.h>
#include <sys/fcntl.h>
#include <unistd.h>

static char *find_debugfs(void)
{
    static char debugfs[MAX_PATH+1];
    static int debugfs_found;
    char type[100];
    FILE *fp;

    if (debugfs_found)
        return debugfs;

    if ((fp = fopen("/proc/mounts","r")) == NULL)
        return NULL;

    while (fscanf(fp, "%*s %"
            STR(MAX_PATH)
            "s %99s %*s %*d %*d\n",
            debugfs, type) == 2) {
        if (strcmp(type, "debugfs") == 0)
            break;
    }
    fclose(fp);

    if (strcmp(type, "debugfs") != 0)
        return NULL;

    debugfs_found = 1;

    return debugfs;
}


void add_trace_marker(char* str) {
    char *debugfs = find_debugfs();
    char path[256];

    if (debugfs) {
        strcpy(path, debugfs);  /* BEWARE buffer overflow */
        strcat(path,"/tracing/trace_marker");
        int trace_fd = open(path, O_WRONLY); /* Enable tracing */
        if (trace_fd >= 0)
            write(trace_fd, str, strlen(str));
            close(trace_fd);
    }
}
#endif