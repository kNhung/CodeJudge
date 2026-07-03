#include <iostream>
using namespace std;

#define MAXROW 100
#define MAXCOL 100
void matrix(int a[][MAXCOL], int n){
	
}


int main(){
	int a[MAXROW][MAXCOL];
	int n, m;
	cin >> n >> m;
	for(int i = 0; i < n; i++){
		for(int j = 0; j < m; j++){
			cin >> a[i][j];
		}
	}
	for(int i = 0; i < n; i++){
		for(int j = 0; j < m; j++){
			cout << a[i][j] << " ";
		}
		cout << endl;
	}
	
	matrix(a, n);
	return 0;
}
