#include <iostream>
#define MAX 10
using namespace std;

void solve2(int a[][MAX], int n, int m){
		for (int i = 0; i < n; i++){
		for (int j = 0; j < m / 2; j++){
			int temp = a[i][j];
			a[i][j] = a[i][m - 1 - j];
			a[i][m - 1 - j] = temp;
		}
	}
}
int main(){
	int a[MAX][MAX];
	int n, m;
	cout << "Input dim: ";
	cin >> n >> m;
	cout << "Input Arr: ";
	for (int i = 0; i < n; i++){
		for (int j = 0; j < m; j++){
			cin >> a[i][j];
		}
	}
	solve2(a, n, m);
	cout << "Output: " << endl;
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < m; j++){
			cout << a[i][j] << " ";
		}
		cout << endl;
	}
	return 0;
}
