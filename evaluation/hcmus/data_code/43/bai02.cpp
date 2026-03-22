# include <iostream>
# include <iostream>
# include <cmath>
# include <string>
# include <cstring>
# include <cstdlib>
# include <stdlib.h>

# define Max 100

using namespace std;

void input (int arr[][Max], int &nRow, int &nCol) {
	for (int i = 0; i < nRow; i++) {
		for (int j = 0; j < nCol; j++) {
			cin >> arr[i][j];
		}
	}
}

void daoMang (int arr[][Max], int &nRow, int &nCol, int arr2[][Max]) {
	int j = nCol;
	
	for (int k = 0; k < nRow; k++) {
		for (int i = 0; i < nCol; i++) {
			if (j > 0) {
				arr2[k][i] = arr[k][j];
				j--;	
			}
		}
	}
}	


void print (int arr[][Max], int nRow, int nCol) {
	for (int i = 0; i < nRow; i++) {
		for (int j = 0; j < nCol; j++) {
			cout << arr[i][j] << " ";
		}
		
		cout << endl;
	}
}

int main () {
	int arr[Max][Max], arr2[Max][Max];
	int n, m;
	
	cout << "Input dim: ";
	cin >> n >> m;
	
	cout << "Input Arr: ";
	input (arr, n, m);
	daoMang (arr, n, m, arr2);
	
	cout << "Output: " << '\n';
	print (arr2, n, m);
	
	return 0;
}
