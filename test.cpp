#include <iostream>
#include <new>
using namespace std;

typedef struct {
    int type;
    void *value;
} var;

int main(int argc, const char* argv[]) {

    cout << "Hello World\n";
    
    var *r = new var[2];

    int *x = new int;
    int *y = new int;

    *x = 1;
    *y = 2;

    r[0].value = x;
    r[1].value = y;

    cout << *((int*) r[0].value) << '\n';
    cout << *((int*) r[1].value) << '\n';

    delete x;
    delete y;
    delete r;
}

