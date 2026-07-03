#include <iostream>
#include <cmath>
using namespace std;
#define MAXROW 40
#define MAXCOL 40
#define MAXN 1000


void inputMat(int Mat[][MAXCOL], int &n, int &row, int &col) {
    cout << "Nhap so phan tu trong mang ";
    cin >> n;

    row = sqrt(n);
    col = sqrt(n);


    cout << "Nhap phan tu mang";
    for (int i = 0; i < row ; i++) {
        for (int j = 0; j < col ; j++) {
            cout << "Mat[" << i << "][" << j << "]= ";
            cin >> Mat[i][j];
        }
    }

}

void printMat(int Mat[][MAXCOL], int row, int col) {
    for (int i = 0; i < row ; i++) {
        for (int j= 0; j < col ; j++) {
            cout << Mat[i][j] << " ";
        }
        cout << endl;
    }

}

bool isDoixungChinh(int Mat[][MAXCOL], int row, int col) {
    for (int i = 0; i < row ; i++) {
        if (Mat[i][row - i - 1] == Mat[row - i - 1][i] ) return true;
        if (Mat[i][i] == Mat[row - i - 1][col - i - 1] ) return true;
        else return false;
    }
    return false;
}

bool isDoixungPhu(int Mat[][MAXCOL], int row, int col) {
    for (int i = 0; i < row ; i++) {
        for (int j = 0; j < col ; j++) {
            if (Mat[i][j] == Mat[row - j - 1][col - i - 1] ) return true;
            if (Mat[i][row - i - 1] == Mat[row - i - 1][i] ) return true;
            else return false;
        }
    }
    return false;
}   



int main() {
    int n, row, col;
    int Mat[MAXROW][MAXCOL];
    

    inputMat(Mat, n, row, col);
    printMat(Mat, row, col);
    if (isDoixungChinh(Mat, row, col) == true)
        cout << "True, Doi xung qua duong cheo chinh";
    else if (isDoixungPhu(Mat, row, col))   
        cout << "True, Doi xung qua duong cheo phu";
    else 
        cout << "False, Khong doi xung";

    cout << row << col;


}