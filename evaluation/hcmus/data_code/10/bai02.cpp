#include <iostream>
#include <cmath>

using namespace std;

int main(){
	int n, m, a[100][100] = {};
	cout << "Input dim: ";
	cin >> n >> m;
	cout << "Input Arr: ";
	for(int i = 0; i < n; i++){
		for(int j = 0; j < m; j++)
			cin >> a[i][j];
		for(int k = 0; k < (m / 2); k++){
			int tem = a[i][k];
			a[i][k] = a[i][m - k - 1];
			a[i][m - k - 1] = tem;
		}
	}
	cout << "Output:" << endl;
	for(int i = 0; i < n; i++){
		for(int j = 0; j < m; j++)
			cout << a[i][j] << " ";
		cout << endl;
	}
	return 0;
}
