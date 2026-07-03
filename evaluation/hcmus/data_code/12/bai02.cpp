#include <iostream>

using namespace std;

void inputMatrix (int matrix[][10], int n, int m) {
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < m; j ++) {
			cin >> matrix [i][j];
		}
	}
}

void printMatrix (int matrix[][10], int n, int m) {
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < m; j ++) {
			if ((i == n - 1) && (j == m - 1)) cout << matrix[i][j];
			else if (j == m - 1) cout << matrix[i][j] << endl;
			else cout << matrix[i][j] << ' ';
		}
	}
}

void Matrixdoixung (int matrix[][10], int n, int m) {
	int temp [n][m];
	
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < m; j ++) {
			temp [i][m - j - 1] = matrix[i][j];
		}
	}

	for (int i = 0; i < n; i++) {
		for (int j = 0; j < m; j ++) {
			matrix[i][j] = temp [i][j];
		}
	}
}

int main() {
	int n, m;
	cout << "Input dim: ";
	do {
		cin >> n >> m;
	} while (n < 1 || m < 1);
	
	int matrix [10][10];
	
	cout << "Input Arr: ";
	inputMatrix (matrix, n, m);
	
	Matrixdoixung (matrix, n, m);
	
	cout << "Output:\n";
	printMatrix (matrix, n, m);
	
	return 0;
}
