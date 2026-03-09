#include <iostream>

using namespace std;

const int MAXN = 40;
const int MAXM = 40;

int main(){
	int n, m;
	int A[MAXN][MAXM];
	int mirrorA[MAXN][MAXM];
	cout << "Input dim: ";
	cin >> n >> m;
	cout << "Input Arr: ";
	for (int i = 0; i < n; i++){
		for (int j = 0; j < m; j++){
			cin >> A[i][j];
		}
	}
	for (int i = 0; i < n; i++){
		for (int j = 0; j < m; j++){
			mirrorA[i][j] = A[i][m - j - 1];
		}
	}
	cout << "Output:";
	for (int i = 0; i < n; i++){
		cout << endl;
		for (int j = 0; j < m; j++){
			cout << mirrorA[i][j] << ' ';
		}
	}
	return 0;
}
