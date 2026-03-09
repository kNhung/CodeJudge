#include <iostream>

using namespace std;

void inputArr (int a[][30], int &m, int &n){
	cout << "Input Arr : ";
	for (int i=0; i<m; i++){
		for (int j=0; j<n; j++){
			cin >> a[i][j];
		}
	}
}

void printArr (int a[][30], int &m, int &n){
	for (int i=0; i<m; i++){
		for (int j=0; j<n; j++){
			cout << a[i][j] << " ";
		}
		cout << endl;
	}
}

void opposite (int a[][30], int m, int n, int b[][30], int b1, int b2){
	int k = b2;
	for (int i=0; i<m; i++){
		for (int j=0; j<n; j++){
			k = n - 1 - j;
			b[i][k] = a[i][j];
		}
	}
}

int main(){
	int m=0, n=0;
	
	do{
		cout << "Input dim : ";
		cin >> m >> n;
		if (m <= 0 || n <= 0)
			cout << "Invalid";
	}while(m <= 0 || n <= 0);
	
	int a[m][30];
	
	int b1=m, b2=n;
	int b[b1][30];
	inputArr (a,m,n);
	
	opposite (a,m,n,b,b1,b2);
	cout << "Output :" << endl;
	printArr (b,b1,b2);
	
	return 0;
}
