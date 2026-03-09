#include <iostream>
using namespace std;


int main(){
	int n,m;
	int a[10000],b[10000];
	
	cout<<"The number of disks: ";
	cin>>n;
	cout<<"The number of changes: ";
	cin>>m;
	for (int i=0;i<n;i++) a[i]=i+1;
	
	cout<<"The order of changes: ";
	
	for (int i=0;i<m;i++) {
		cin>>b[i];
		for (int j=0;j<n;j++){
	    	if (b[i]==a[j]){
			     for (int z=j;z>0;z--){
		      		a[z]=a[z-1];
		        }
			a[0]=b[i];
		    }
     	}
	
  
    } 
	
	
	cout<<"Disk stack: ";
	for (int i=0;i<n;i++) cout<<a[i]<<" ";
	
	return 0;
}
