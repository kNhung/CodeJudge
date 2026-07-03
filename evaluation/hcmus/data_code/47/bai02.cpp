#include <iostream>

using namespace std;

void input(int a[100][100], int n, int m){
	cout << "Input Arr: ";
	for(int i = 0; i < n; i++){
		for(int j = 0; j < m; j++){
			cin >> a[i][j];
		}		
	}
}

void output(int a[100][100], int n, int m){
	for(int i = 0; i < n; i++){
		for(int j = 0; j < m; j++)
			cout << a[i][j] << " ";
		cout << endl;
	}

}


int main(){
	int n,m;
	cout << "Input dim: ";
	cin >> n >> m;
	
	int a[100][100];
	int b[100][100];
	input(a,n,m);

	
	for(int i = 0; i < n; i++){
		for(int j = 0; j < m; j++){
			b[i][m-1-j] = a[i][j];
		}
	}
	cout << "Output: " << endl;
	output(b,n,m);
	
	return 0;
}
