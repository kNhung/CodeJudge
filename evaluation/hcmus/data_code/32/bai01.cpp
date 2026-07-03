#include <iostream>
#include <cmath>
#include <string>
#include <cstring>
#include <cstdlib>
#include <stdlib.h>
using namespace std;
void Addto(int a[], int&n, int pos,int val){
	for (int i = n - 1; i >= pos; i-- ){
		a[i+ 1] = a[i]; 
	}
	a[pos] = val;
	n++;
}
void deleteAt (int a[], int &n, int pos){
	for (int i = pos; i < n - 1; i++){
		a[i] = a[i+1];
	}
	n--;
}

void sortDisks (int a[] ,int &n, int nChange){
	for (int i=0; i< n; i++ ){
		if (a[i] == nChange);
	
		deleteAt(a,n, i);
		Addto (a,n,0,nChange);
		break;
	}
	
			
		
			
}



int main(){
	int a[10000];
	int n;
	cout <<"Input number of disks: ";
	cin >> n;
	
	
	int nChanges;
	cout <<"Input number of changes: ";
	cin >> nChanges;
	
	int num[10000];
	
	cout <<"The order of changes: ";
	for (int i = 0; i < nChanges; i++){
		cin >> num[i];
	
	}
	for (int i = 0; i < nChanges; i++){
		sortDisks (a,n,num[i]);
	}
	cout << "Disk stack: ";
	for (int i = 0; i<n;i++){
		cout <<a[i]<<" ";
	}
	return 0;
}
