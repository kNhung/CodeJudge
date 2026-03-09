#include <iostream>
#include <cmath>
#include <string>
#include <cstdlib>
#include <fstream>

using namespace std;

void printArr(int arr[][100], int m, int n){
	for (int i = 0; i < m; i++){
		for (int j = 0; j < n; j++){
			cout << arr[i][j] << " ";
		}
		cout << endl;
	}
}

void changes(int arr[][100], int m, int n){
	int temp[100][100];
	for (int i = 0; i < m; i++){
		for (int l = 0; l < n; l++){
			//cout << l;
			temp[i][l] = arr[i][n - l - 1];
		}
	}
	for (int i = 0; i < m; i++){
		for (int j = 0; j < n; j++){
			arr[i][j] = temp[i][j];
		}
	}
}


int main(){
	int m, n;
	cout << "Input dim: ";
	cin >> m >> n;
	cout << "Input Arr: ";
	int arr[100][100];
	for (int i = 0; i < m; i++){
		for (int j = 0; j < n; j++){
			cin >> arr[i][j];
		}
	}
	changes(arr, m, n);
	printArr(arr, m, n);
	//system("pause");
	return 0;
}