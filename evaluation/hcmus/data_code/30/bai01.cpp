#include <iostream>
#include <math.h>
#include <cstring>
#include <string>
#include <cstdlib>

using namespace std;


int FindkPos(int a[], int &n, int k){
	int pos;
	for(int i = 0; i < n; i++){
		if(a[i] == k) pos = i;
	}
	return pos;
}
void SapXepLai(int a[], int &n, int k){
	int nk = FindkPos(a, n, k);
	for(int i = nk; i > 0; i--){
		a[i] = a[i -1];
	}
	a[0] = k;
}

int main(){
	int n, m;
	int change[100], dia[100];
	cout << "Input number of disks: "; cin >> n;
	for(int i = 0; i < n; i++){
		dia[i] = i + 1;
	}
	cout << "Input number of changes: "; cin >> m;
	cout << "The order of changes: ";
	for(int i = 0; i < m; i++){
		cin >> change[i];
		SapXepLai(dia, n, change[i]);
	}
	cout << "Disk stack: ";
	for(int i = 0; i < n; i++){
		cout << dia[i];
	}	
	return 0;
}
