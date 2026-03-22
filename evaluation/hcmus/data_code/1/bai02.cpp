#include<iostream>
#include<cstring>
#include<fstream>
using namespace std;



void inputMatrix(int a[][100], int &n, int &m) {
	for (int i=0; i < n; i++) {
		for (int j = 0; j < m; j++) {
			cin >> a[i][j];
		}		
	}
}

void printMatrix(int a[][100], int n, int m) {
	for (int i=0; i < n; i++) {
		for (int j = 0; j < m; j++) {
			cout  << a[i][j] << " ";
		}		
		cout << endl;
	}
}

void matrixDoixung(int a[][100], int n,int  m) {
	int b[100][100];
	for (int i=0; i < n; i++) {
		for (int j = 0; j < m; j++) {
			b[i][m-j-1] = a[i][j];
		}		
	}
	
	printMatrix(b, n, m);
}
int main() {
	int a[100][100];
	int n, m;
	cout << "Input dim: ";
	cin >> n >> m;
	cout << "Input Arr: ";
	inputMatrix(a, n, m);
	printMatrix(a, n, m);
	matrixDoixung(a, n, m);
	
	return 0;
}
