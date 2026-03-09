#include <iostream>
#include <cmath>

#define MAXCOL 10
#define MAXROW 10

using namespace std;

void inputMat(int a[][MAXCOL], int& n, int& nRow, int& nCol){
	cout << "Nhap so phan tu cua mang: ";
	cin >> n;
	nRow = nCol = sqrt(n);
	for (int i = 0; i < nRow; i++)
		for (int j = 0; j < nCol; j++){
			cin >> a[i][j];
		}
}

bool KiemTraDuongCheoChinh(int a[][MAXCOL], int n, int nRow, int nCol) {
	for(int i = 0; i < nRow; i++) {
		for(int j = 0; j < nCol; ++j) {
			if(a[i][j] != a[j][i]) {
				return 0;
			}
			else {
				return 1;
			}
		}
	}
	return 1;
}

bool KiemTraDuongCheoPhu(int a[][MAXCOL], int n, int nRow, int nCol) {
	for(int i = nRow - 1; i >= 0; i++) {
		for(int j = nCol - 1; j >= 0; j++) {
			if(a[i][j-1] != a[j-1][i]) {
				return 0;
			}
			else {
				return 1;
			}
		}
	}
	return 1;
}

int main() {
	int a[MAXROW][MAXCOL];
	int n;
	int nRow, nCol;
	inputMat(a, n, nRow, nCol);
	
	if(KiemTraDuongCheoChinh(a, n, nRow, nCol)) {
		cout << "True";
	}
	else if(KiemTraDuongCheoPhu(a, n, nRow, nCol)) {
		cout << "True";
	}
	else {
		cout << "False";
	}
	
	return 0;
}