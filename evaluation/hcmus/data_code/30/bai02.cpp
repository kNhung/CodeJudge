#include <iostream>
#include <math.h>
#include <cstring>
#include <string>
#include <cstdlib>

using namespace std;
int main(){
	int a[100][100];
	int m, n;
	cout << "Input dim: ";
	cin >> m;
	cin >> n;
	cout << "Input Arr: ";
	for(int i = 0; i < m; i++){
		for(int j = 0; j < n; j++){
			cin >> a[i][j];
		}
	}
	int b[100][100];
	for(int i = 0; i < m; i++){
		for(int j = 0; j < n; j++){
			b[i][j] = a[i][n - 1 - j];
		}
	}
	for(int i = 0; i < m; i++){
		for(int j = 0; j < n; j++){
			cout << b[i][j] << " ";
		}
		cout << endl;
	}
	return 0;
}
