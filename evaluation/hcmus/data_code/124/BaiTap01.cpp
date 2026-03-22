#include <iostream>
#using namespace std;

bool isDiagonalSymmetric(int matrix[][100], int n) {

    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (matrix[i][j] != matrix[j][i]) {
                return false;
            }
        }
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (matrix[i][j] != matrix[n - j - 1][n - i - 1]) {
                return false;
            }
        }
    }

    return true;
}

int main() {
    int n;
    cout << "Nhap kich thuoc ma tran n x n: ";
    cin >> n;


    int matrix[100][100];

    cout << "Nhap cac phan tu cua ma tran:\n";
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            cin >> matrix[i][j];
        }
    }

    bool isSymmetric = isDiagonalSymmetric(matrix, n);

    if (isSymmetric) {
        cout << "Ma tran doi xung qua duong cheo chinh hoac duong cheo phu.\n";
    } else {
        cout << "Ma tran khong doi xung qua duong cheo chinh hoac duong cheo phu.\n";
    }

    return 0;
}