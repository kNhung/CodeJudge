#include<iostream>
using namespace std;
int main(){
	int n, k, a[100], disks[100];
	cout<<"Input number of disks: ";
	cin>>n;
	cout<<"Input number of changes: ";
	cin>>k;
	cout<<"The order of changes: ";
	for (int i=0; i<k; i++){
		cin>>a[i];
	}
	for (int i=0; i<n; i++){
		disks[i]=i+1;
	}
	for (int i=0; i<k; i++){
		for (int j=a[i]-1; j>=0; j--){
			disks[j]=disks[j-1];
		}
		disks[0]=a[i];
	}
	for (int i=0; i<n; i++){
		cout<<disks[i]<<' ';
	}
	return 0;
}
