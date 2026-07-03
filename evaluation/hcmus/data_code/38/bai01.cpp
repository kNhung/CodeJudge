#include <iostream>
using namespace std;

void inputArr(int a[], int n){
	for(int i = 0; i < n; i ++){
		cin>>a[i];
	}
}

void outputArr(int a[], int n){
	for(int i = 0; i < n; i++){
		cout<<a[i];
	}
}

void changeOrder(int a[], int n){
	int pos;
	cin>>n;
	int temp;
	for(int i = 0; i < n; i++){
		if(i == pos-1){
			a[i] = a[0];
		}
	}
	outputArr(a, n);
	
}


int main(){
	int disk;
	cout<<"Input number of disks: ";
	cin>>disk;
	int a[disk];
	inputArr(a, disk);
	int change;
	cout<<"Input number of changes: ";
	cin>>change;
	cout<<"The order of changes: ";
	changeOrder(a, disk);
	cout<<"Disks stack: ";
	
	
	return 0;
}
