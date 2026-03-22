#include <iostream>
using namespace std;

int main(void){
	int a[100][100], b[100][100], n, m;
	cout << "Input dim: ";
	cin >> n >> m;
	cout << "Input Arr: ";
	for (int i = 0; i < n; i++){
		for (int j = 0; j < m; j++){
			cin >> a[i][j];
		}
	}
	for (int i = 0; i < n; i++){
		for (int j = 0; j < m; j++){
			b[i][j] = a[i][m - j - 1];
		}
	}
	cout << "Output: " << endl;
	for (int i = 0; i < n; i++){
		for (int j = 0; j < m; j++){
			cout << b[i][j] << " ";
		}
		cout << endl;
	}
}
