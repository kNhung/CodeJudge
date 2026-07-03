#include <iostream>
#include<cmath>
#include<cstring>
using namespace std;

const int MAX_SIZE = 100;

void inputarr(int a[MAX_SIZE][MAX_SIZE], int n) {
    for (int i = 0; i < sqrt(n); i++) {
        for (int j = 0; j < sqrt(n); j++) {
            cout << "a[" << i << "," << j << "]: ";
            cin >> a[i][j];
        }
    }
}

void outputarr(int a[MAX_SIZE][MAX_SIZE], int n) {
    for (int i = 0; i < sqrt(n); i++) {
        for (int j = 0; j < sqrt(n); j++) {
            cout << a[i][j] << " ";
        }
        cout << endl;
    }
}

bool duongcheochinh(int a[MAX_SIZE][MAX_SIZE], int n) {
    for (int i = 0; i < sqrt(n); i++) {
        for (int j = 0; j < sqrt(n); j++) {
            if (a[i][j] == a[j][i]) {
                return true;
            }
        }
    }
    return false;
}

bool duongcheophu(int a[MAX_SIZE][MAX_SIZE], int n) {
    for (int i = 0; i < sqrt(n); i++) {
        for (int j = 0; j < sqrt(n); j++) {
            if (a[i][j] == a[n - 1 - j][n - 1 - i]) {
                return true;
            }
        }
    }
    return false;
}

int main() {
    int a[MAX_SIZE][MAX_SIZE];
    int n;
    cin >> n;
    inputarr(a, n);
    outputarr(a, n);
    if (duongcheophu(a, n)) {
        cout << "True";
    }
    else
        cout << "False";
    return 0;
}
