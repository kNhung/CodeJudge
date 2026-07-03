#include <iostream>
using namespace std;

void inputMatrix (int a[][100], int n, int m){
	for (int i = 0; i < n; i++){
		for (int j = 0; j < m; j++){
			cin >> a[i][j];
		}
	}
}

void printMatrix (int a[][100], int n, int m){
	for (int i = 0; i < n; i++){
		for (int j = 0; j < m; j++){
			cout << a[i][j] << " ";
		}
		cout << endl;
	}
}

void findOppMatrix (int a[][100], int n, int m){
	for (int i = 0; i < n; i++){
		for (int j = 0; j < m / 2; j++){
			swap(a[i][j], a[i][m - j - 1]);
		}
	}
}

int main (){
	int a[100][100];
	int n, m;
	do{
		cout << "Input dim: ";
		cin >> n >> m;
	} while (n <= 0 || m <= 0);
	cout << "Input Arr: ";
	inputMatrix(a, n, m);
	findOppMatrix(a, n, m);
	printMatrix(a, n, m);
	return 0;
}
