#include <iostream>
using namespace std;

int main() {
	int a[10][10], b[10][10], r, c;
	cout << "Input dim: ";
	cin >> r >> c;
	for (int i = 0; i < r; i++) {
		for (int j = 0; j < c; j++) {
			cin >> a[i][j];
		}
	}
	int c1 = 0;
	for (int i = 0; i < r; i++) {
		for (int j = c - 1; j >= 0; j--) {
			b[i][c1++] = a[i][j];
		}
		c1 = 0;
	}
	
	for (int i = 0; i < r; i++) {
		for (int j = 0; j < c; j++) {
			cout << b[i][j] << " ";
		}
		cout << endl;
	}
	return 0;
}
