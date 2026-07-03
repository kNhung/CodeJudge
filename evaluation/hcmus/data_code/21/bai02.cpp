#include <iostream>
#include <cmath>
using namespace std;
void Nhap_mang( int a[][100], int &n , int &m){
	for ( int i = 0; i < n; i++ ){
		for(int j = 0; j < m; j++){
			cin >> a[i][j];
		}
	}
}
void XuLiMang( int a[][100], int &n, int &m){
    for ( int i = 0; i < n ; i++){
    	if (i % 2 == 0){
    		for (int j = m - 1; j >= 0; j--){
    			cout << a[i][j] << " ";
			}
			cout << endl;
	    }
		else{
			for ( int j = 0; j < m; j++){
				cout << a[i][j] << " ";
			}
		}
		
	}
}


int main(){
	int n,m;
	int a[100][100];
	cout << "Input dim: ";
	cin >> n >> m;
	cout << "Input Arr: ";
	Nhap_mang(a,n,m);
	cout << "Output:" << endl;
	XuLiMang(a,n,m);
	return 0;
}
