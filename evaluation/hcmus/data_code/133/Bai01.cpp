#include <iostream>
#include <cmath>

using namespace std;

void addArray(int a[][100], int&n) {
    cin >> n;
    int m = sqrt(n);
    if (m * m == n) {
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < m; j++) {
                cin >> a[i][j];
            }
        }
    }
}

void kiemtradoixung(int a[][100], int n) {
    int m = sqrt(n) - 1;
    int flag = -1;
    for (int i = 0; i < m + 1; i++) {
        if (a[0][0] = a[m][m]) {
            for (int j = 0; j < m; j++) {
                if (a[j][] == a[m ])
            }
        }
    }
}

int main() {
    int a[100][100];
    int n;
    addArray(a, n);
    return 0;
}