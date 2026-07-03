#include <iostream>
#include <cmath>
#include <fstream>
#include <string>
using namespace std;
int main(){
	int n,m;
	cout<<"Input dim: ";
	cin>>n>>m;
	int a[n][m];
	cout<<"Input Arr: ";
	for(int i= 0; i<n; i++){
		for(int j =0; j<m; j++){
			cin>>a[i][j];
		}
	}
	cout<<"Output: "<<endl;
	for(int i= 0; i<n; i++){
		for(int j =m-1; j>=0; j--){
			cout<<a[i][j]<<" ";
		}
		cout<<endl;
	}
	

	return 0;
}
