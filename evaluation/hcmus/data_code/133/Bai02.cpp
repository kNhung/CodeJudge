#include <iostream>
#include <cstring>

using namespace std;

bool kiemtra(char a[]) {
    int n = strlen(a);
    for (int i = 1; i < n; i++) {
        char b = a[i];
        if (i == 0) {
            if (b == a[1]) {
                return 1;
                break;
            }
        } else if (i == n) {
            if (b == a[n - 2]) {
                return 1;
                break;
            }
        } else {
            if (b == a[i - 1] || b == a[i + 1]) {
                return 1;
                break;
            } else return 0;
        }
    }
}

void xoachucaitrung(char a[]) {
    int n = strlen(a);
    for (int i = 0; i < n; i++) {
        char b = a[i];
        if (kiemtra(b) == 1) {
            
        }
    }
}

int main() {
    char a[100];
    cin >> a;
}