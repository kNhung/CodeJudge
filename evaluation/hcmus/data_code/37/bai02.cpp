#include <iostream>
#include <fstream>
#include <cstring>
#include <string.h>
#include <stdlib.h>
#define max 100
using namespace std;

int main(){
	int n,m;
	int a[max][max];
	cout << "input dim: ";
	cin >> n >> m;
	cout << "input arr:";
	for (int i = 0; i < n; i++){
		for (int j = m - 1; j >= 0; j--){
			cin >> a[i][j];
		}
	}
	cout << "output :" << endl;
	for (int i = 0; i  < n ; i++){
		for (int j = 0; j < m; j++){
			cout  << a[i][j] << "\t";
		}
		cout << endl;
	}
	return 0;
}
