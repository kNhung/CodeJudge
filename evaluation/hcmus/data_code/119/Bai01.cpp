#include <iostream>
#include <cmath>
using namespace std;

bool isDiagonalSymmetric(int a[][1000], int n, int m) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (a[i][j] != a[j][i]) {
                return false;
            }
        }
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (a[i][j] != a[m - 1 - j][n - 1 - i]) {
                return false;
            }
        }
    }

    return true;
}

int main() {
    int a[1000][1000];
    int x;
    cin >> x;

    int n = sqrt(x);
    int m = sqrt(x);

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            cin >> a[i][j];
        }
    }

    if (isDiagonalSymmetric(a, n, m)) {
        cout << "True";
    }
    else {
        cout << "False";
    }

    return 0;
}