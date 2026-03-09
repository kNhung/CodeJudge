#include<iostream>
#include<cmath>
#include<cstring>

using namespace std;

int main()
{
	 int a[10000];
	int n;
	int b[10000];
	int m;
	 cout<<"\n nhap so luong dia:=";
	cin>>n;
	int j=1;
	for(int i=0; i<n; i++){
		a[i]= j;
		j++;
	}
//	for(int i=0; i<n; i++){
//		cout<<a[i]<<", ";
//	}
	cout<<"\n nhap so luong dia muon nghe:=";
	cin>>m;
	for(int i=0; i<m; i++){
		cout<<"\n nhap dia muon nghe:";
		cin>>b[i];
	}
	for(int i=0; i<m; i++){
		for(int j=0; j<n; j++){
			if(b[i]==a[j]){
				
				for(int k=j; k>=1; k--){
					a[k]=a[k-1];
				}
				a[0]=b[i];
				break;
			}
		}
	}
	for(int v=0; v<n; v++){
		cout<<a[v]<<", ";
	}
	 return 0;
}
