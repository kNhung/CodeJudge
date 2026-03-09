#include <iostream>
#include <cmath>
using namespace std;
//bai1


int main(){
	int a[1000][1000];
	int m, n;
	cin >> m;
	n = sqrt(m);
	for (int i = 0; i <= n; ++i){
		for (int j = 0; j <= n; ++j){
			cin >> a[m][n];
		}
	}
	for (int k = 0; k <= n; ++k){
		for (int l = n; l >= 0; l--){
			if(a[k][l] - a[l][k] == 0){
				cout << "TRUE";
				return 0;
			}
			else{
				if (a[k][l] - a[k+1][l+1] == 0){
					cout << "TRUE";
				}
				cout << "FALSE";
			}
		}
	}
	return 0;
}


