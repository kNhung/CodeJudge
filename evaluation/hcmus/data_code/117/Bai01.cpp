#include <iostream>
#include <cmath>

using namespace std;

void inputMatrix(int a[][100], int n) {
    for (int h = 0; h < n; h++) {
        for (int c = 0; c < n; c++) {
            cin >> a[h][c];
        }
    }
}

bool check (int a[][100], int n) {
    bool flag = true;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if ((i != j)){
                if ((a[i][j] != a[j][i])) {
                    flag = false;
                }
            }
        }
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if ((i != (n - j))){
                if ((a[i][j] == a[n - j - 1][n - i - 1])) {
                    flag = true;
                }
            }
        }
    }
    return flag;
}

int main() {
    int m;
    cin >> m;
    int n = sqrt(m);
    int a[100][100];
    inputMatrix(a, n);
    int ktr = check(a, n); 
    if (ktr == 1) cout <<"TRUE";
    else cout << "FALSE";
    return 0;
}