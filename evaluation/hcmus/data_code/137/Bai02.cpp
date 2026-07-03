#include <iostream>
#include <cstring>
#include <cmath>
using namespace std;

#define MAX 100

void xoa(char a[]) {
    int n = strlen(a);
    int k = 0;
    for (int i = 0; a[i] != '\0'; i++) {
        if (k == 0 || a[i] != a[k - 1]) {
            a[k] = a[i];
            k++;
        } else {
            k--;
        }
    }
    a[k] = '\0';
}


int main() {
    char a[MAX];
    cin >> a;
    
    xoa(a);
    cout << a << endl;
    return 0;
}