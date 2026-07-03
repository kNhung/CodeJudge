#include <iostream>
#include <cmath>
#include <fstream>
#include <string>
using namespace std;
int main(){
	int n;
	cout<<"Input number of disks: ";
	cin>>n;
	int a[n];
	for(int i=0; i<n; i++){
		cin>>a[i];
	}
	int m;
	cout<<"Input number of changes: ";
	cin>>m;
	
	
	cout<<"The order of changes: ";
	int b[m];
	int c [n+m];
	for(int i=0; i<n; i++){
		for(int j=0; j<m; j++){
			cin>>b[j];
			for(int k = 0; k<n+m; k++){
				c[k] = b[j] + a[i];
			}	
		}
	}
	
	
	for(int k = 0; k<n+m; k++){
			cout<< c[k] <<" ";
		}
	return 0;
}
