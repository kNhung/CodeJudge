#include <iostream>
#include <cmath>

using namespace std;

const int MAX = 100;

void inputArray(int a[][MAX], int &n){
	cout<< "Nhap vao so phan tu: ";
	cin >> n;
	
	for (int i = 0; i < (int)sqrt(n); i++){
		for (int j = 0; j < (int)sqrt(n); j++){
			cin >> a[i][j];
		}
	}
}

bool solve(int a[][MAX], int n){
	for (int i = 0; i < n; i++){
		for (int j = 0; j < n; j++){
			if (i == n - 1 - j){
			    if (i == 0 && j == 0){
				    if (a[i][j] != a[(int)sqrt(n) - 1][(int)sqrt(n) - 1]){
					    return 0;
				    }
			    }
			
			    if (a[i][j] != a[i + 1][j + 1]){
				    return 0;
			    }
			
			    if (a[i][j] != a[j][i]){
				    return 0;
			    }   
			}
			
			if (i == j){
				if (a[i][n - 1 - j] != a[n - 1 - j][i]){
				    return 0;
			    }
			}
		}
	}
	
	return 1;
}

int main(){
	int a[MAX][MAX];
	int n;
	inputArray(a, n);
	cout << solve(a, n);
	
	return 0;
}
