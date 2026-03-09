#include <iostream>
#include <cmath>
using namespace std;

void getInput(int mat[100][100], int n){
    for (int row = 0; row < n; ++row)
        for (int col = 0; col < n; ++col)
            cin >> mat[row][col];
}

int checkDoiXung(int mat[100][100], int n){
    // duong cheo chinh
    int checkChinh = 1;
    for (int row = 0; row < n - 1 ; ++row)
        for (int col = row+1; col < n; ++col)
            if (mat[row][col] != mat[col][row]) checkChinh = 0;
    // duong cheo phu
    int checkPhu = 1;
    for (int row = 0; row < n-1; ++row)
        for (int col = 0; col < n-row-1; ++col)
            if (mat[row][col] != mat[n-col-1][n-row-1]){
                checkPhu = 0;
            }
        
    return checkChinh+checkPhu;
}

int main(){
    int mat[100][100];
    int n;
    cin >> n;
    getInput(mat,sqrt(n));
    int check = checkDoiXung(mat,sqrt(n));
    if (check) cout << "True";
    else cout << "False";
    return 0;
}