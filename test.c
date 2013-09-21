#include <stdio.h>
#include <stdlib.h>

#define LENGTH 2

typedef struct {
    int type;
    void *value;
} var;

int main(int argc, const char* argv[]) {

    printf("Hello World\n");
    
    var *r = (var*) malloc(LENGTH*sizeof(var));

    int *x = malloc(sizeof(int));
    int *y = malloc(sizeof(int));

    *x = 1;
    *y = 2;

    r[0].value = x;
    r[1].value = y;

    printf("%d\n",  *((int*) r[0].value));
    printf("%d\n",  *((int*) r[1].value));

    free(x);
    free(y);
    free(r);
}

