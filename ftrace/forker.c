#include <stdio.h>
#include <unistd.h>
#include<stdlib.h>
#include<sys/wait.h>

int main(){
    sleep(60);
    int child = fork();

    if(child == 0) {
        printf("In child");
    }
    else{
        printf("In parent");
        wait(NULL);
    }
    sleep(60);
    return 0;
}