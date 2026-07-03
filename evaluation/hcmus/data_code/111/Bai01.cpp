/*
Ho ten: Le Nguyen Nhat Truong
Lop: 23CLC02
MSSV: 23127136

Chuong trinh: kiem tra doi xung qua duong cheo chinh hoac phu
*/


#include <iostream>
#include <cmath>

using namespace std;

const int MAX_ROW = 10;
const int MAX_COL = 10;

void inputArray(int a[][MAX_COL], int& n) {
    int soPhanTu;
    cin >> soPhanTu;

    n = sqrt(soPhanTu);

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            cin >> a[i][j];
        }
    }
}

bool ktraDoiXungChinh(int a[][MAX_COL], int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (a[i][j] != a[j][i]) return false;
        }
    }
    return true;
}

bool ktraDoiXungPhu(int a[][MAX_COL], int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (a[i][j] != a[n - j - 1][n - i - 1]) return false;
        }
    }
    return true;
}

bool ktraDoiXung(int a[][MAX_COL], int n) {
    return (ktraDoiXungChinh(a, n) || ktraDoiXungPhu(a, n));
}

int main() {
    int a[MAX_ROW][MAX_COL] = { {1, 1, 2, 2, 2}, 
                                {2, 1, 1, 2, 2},
                                {2, 1, 1, 1, 2},
                                {2, 2, 1, 1, 1},
                                {1, 2, 2, 2, 1}};
    int size;

    inputArray(a, size);

    cout << (ktraDoiXung(a, size) ? "True" : "False");

    return 0;
}