#include <iostream>
#include <cmath>
using namespace std;
void nhapMang(int a[100][100], int &n, int &m) {
	cout << "Input dim: ";
	cin >> n;
	cin >> m;
	cout << "Input Arr: ";
	for (int i = 0; i < n; i++) {
		for(int j = 0; j < m; j++) {
			cin >> a[i][j];
		}
	}
}
void xuatMang(int a[][100], int n, int m) {
	for (int i = 0; i < n; i++) {
		for(int j = 0; j < m; j++) {
			cout << a[i][j] << " ";
		}
		cout << endl;
	}
}
int main() {
	int n, m;
	int a[100][100];
	nhapMang(a, n, m);
	int b[100][100];
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < m; j++) {
			b[i][j] = a[i][m-1-j];
		}
	}
	cout << "Output: " << endl;
	xuatMang(b, n, m);
	return 0;
}
