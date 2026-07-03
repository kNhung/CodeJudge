#include <iostream>

using namespace std;

void input(int a[], int n){
	for(int i = 0; i < n; i++){
		a[i] = i+1;
	}
}
void inputChange(int a[], int n){
	for(int i = 0; i < n; i++){
		cin >> a[i];
	}
}
void output(int a[], int n){
	for(int i = 0; i < n; i++){
		cout << a[i] << " ";
	}
}

void changes(int a[], int n, int idx){
	for(int i = idx-1; i >= 0; i--){
		a[i] = a[i-1];
	}
	a[0] = a[idx];
}
int main(){

	int n;
	cout << "Input number of disks: ";
	cin >> n;
	int m;
	cout << "Input number of changes: ";
	cin >> m;
	int change[m];
	int disks[10000];
	
	input(disks, n);
	cout << "The order of changes: ";
	inputChange(change,m);

	for(int i = 0; i < m; i++){
		changes(disks,n,change[i]);

	}
	cout << "Disk stack: ";
	output(disks,n);
	
	return 0;
}
