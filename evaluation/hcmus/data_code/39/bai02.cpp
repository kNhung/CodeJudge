#include <iostream>
using namespace std;
void symMatrix(int a[][10], int b[][10], int m, int n){
	for (int i=0; i<m; i++){
		for ( int j=0; j<n; j++){
			b[i][m-j-1]= a[i][j];
		}
	}
}

void print(int a[][10],int m,int n, int b[][10]){
for (int i=0; i<m; i++){
	for (int j=0; j<n; j++){
		cout << b[i][j]<< " ";
	}
	cout << endl;
}
}
int main(){
int a[10][10];
int b[10][10];
int m, n;
cout <<"Input dim: ";
cin >> m >> n; cout << endl;
cout <<"Input Arr: ";
for (int i=0; i<m; i++){
	for (int j=0; j<n; j++){
		cin>> a[i][j];
	}
}
symMatrix(a,b,m,n);
cout << "Output:\n";
print (a,m,n,b);
return 0;	 
}

