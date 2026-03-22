#include<iostream>
#include<string>
#include<cmath>
using namespace std;

int main(){
	int n, m;
	cout << "Input dim: ";
	cin >> n >> m;
	int a[n][m];
	cout << "Input Arr: ";
	for (int i = 0; i < n; i++)
		for (int j = 0; j < m; j++) cin >> a[i][j];
	int b[n][m];
	int bj = m - 1;
	for (int i = 0; i < n; i++){
		for (int j = 0; j < m; j++){
			b[i][bj] = a[i][j];
			bj--;
		}
		bj = m - 1;
	}
	cout << "Output:\n";
	for (int i = 0; i < n; i++){
		for (int j = 0; j < m; j++) cout << b[i][j] << ' ';
		if (i != n - 1)cout << '\n';
	}
	return 0;
}
