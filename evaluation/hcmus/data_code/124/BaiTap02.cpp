#include <iostream>
#include <cstring>

#define MAX 1000

using namespace std;

void xoakitutrunglap(char a[], int& len) {
    int i = 0;
    while (i < len - 1) {
        if (a[i] == a[i + 1]) {
            for (int j = i; j < len - 1; j++) {
                a[j] = a[j + 2];
            }
            len -= 2;
        } else {
            i++;
        }
    }
}

int main() {
    char a[MAX] = "helloo";
    int len = strlen(a);

    xoakitutrunglap(a, len);

    for (int i = 0; i < len; i++) {
        cout << a[i];
    }

    return 0;
}