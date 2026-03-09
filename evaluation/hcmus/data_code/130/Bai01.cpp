#include <iostream>
#include <cmath>

using namespace std;

const int MAX = 100;

void nhapMaTran(int a[][MAX], int &n) {
	do {
		cout << "Nhap n: ";
		cin >> n;
	} while(n < 0);
	n = sqrt(n);
	for(int i = 0; i < n; i++) {
		for(int j = 0; j < n; j++) {
			cin >> a[i][j];
		}
	}
}

void xuatMaTran(int a[][MAX], int n) {
	for(int i = 0; i < n; i++) {
		for(int j = 0; j < n; j++) {
			cout << a[i][j] << "\t";
		}
		cout << endl;
	}
}

int ktrDoiXungChinh(int a[][MAX], int n) {
	for(int i = 0; i < n; i++) {
		for(int j = 0; j < n; j++) {
			if(i != (n - 1 - j)) {
				if(a[i][j] != a[n - 1 - j][n - 1 - i]) return 0;
			}
		}
	}
	return 1;
}

int ktrDoiXungPhu(int a[][MAX], int n) {
	for(int i = 0; i < n; i++) {
		for(int j = 0; j < n; j++) {
			if(i != j) {
				if(a[i][j] != a[j][i]) return 0;
			}
		}
	}
	return 1;
}

int ktrDoiXungQuaDuongCheo(int a[][MAX], int n) {
	if(ktrDoiXungPhu(a, n) || ktrDoiXungChinh(a, n)) return 1;
	return 0;
}

int main() {
	int ma_tran[MAX][MAX];
	int n;
	
	nhapMaTran(ma_tran, n);
	xuatMaTran(ma_tran, n);
	cout << ktrDoiXungQuaDuongCheo(ma_tran, n);
	
	return 0;
}
