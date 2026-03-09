#include <iostream>
#include <cmath>

using namespace std;

const int MAX = 10;

bool checkValidInput(int n) {
	int a = sqrt(n);
	float b = sqrt(n);
	
	if (a == b) {
		return true;
	} else {
		cout << "Hay nhap lai!" << endl;
		return false;
	}
}

void input2dArr(int a[][MAX], int &n) {
	do {
		cin >> n;
	} while (!checkValidInput(n));

	int m = sqrt(n);
	
	for (int i = 0; i < m; i++) {
		for (int j = 0; j < m; j++) {
			cin >> a[i][j];
		}
	}
}

bool ktraDoiXung(int a[][MAX], int n) {
	int m = sqrt(n);
	
	for (int i = 0; i < m; i++) {
		for (int j = 0; j < m - i - 1; j++) {
			if (a[i][j] != a[m - j - 1][m - i - 1]) {
				return false;
			}
		}
	}
	
	return true;
}

int main () {
	int arr[MAX][MAX];
	int n;
	
	input2dArr(arr, n);
	if (ktraDoiXung(arr, n)) {
		cout << "True";
	} else {
		cout << "False";
	}
	
	return 0;
}
