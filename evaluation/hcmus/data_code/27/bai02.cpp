#include <iostream>
using namespace std;

void reflectMatrix(int a[][200], int b[][200], int n, int m) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            b[i][m - j - 1] = a[i][j];
        }
    }
}

void printArr(int a[][200], int n, int m) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            cout << a[i][j] << " ";
        }
        cout << "\n";
    }
}

int main() {
    int m, n;
    cout << "Input dim: ";
    cin >>  n >> m;
    int a[200][200];
    int b[200][200];
    cout << "Input arr: ";
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            cin >> a[i][j];
        }
    }
    reflectMatrix(a, b, n, m);
    printArr(b, n, m);
    return 0;
}

