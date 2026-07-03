#include <cstring>
using namespace std;
#include <iostream>
void toFront(int a[], int n, int b){
	int pos=b-1;
	
	for (int j=pos; j<n-1; j++){
		a[j]=a[j+1];
	}
	for ( int z =n-1; z>0; z--){
		a[z]= a[z-1];
	}
	a[0]=b;
}

int main(){
	int n, b;
	int changes;
	cout <<"Input number of disks: ";
	cin >>n; cout <<endl;
	int a[10];
	for (int e=1; e<=n; e++){
		a[e-1]=e;
	}
	cout << "Input number of changes: ";
	cin >> changes; cout <<endl;
	cout << "The order of changes: ";
	for (int i=0; i<changes; i++){
		cin >> b;
		toFront(a, n, b);
	} cout <<"Disk stack: ";
	for (int j=0; j<n; j++) cout << a[j];
	return 0;
}

