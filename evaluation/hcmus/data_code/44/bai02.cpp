#include <iostream>
using namespace std;

int main(){
	int a[100][100],b[100][100];
	int n,m,val;
	
	cout<<"Input dim: ";
	cin>>n>>m;
	cout<<"Input Arr: ";
	
	for (int i=0;i<n;i++){
		for (int j=0;j<m;j++)
		    cin>>a[i][j];
	}
	
	for (int i=0;i<n;i++){
		val=0;
		for (int j=m-1;j>-1;j--){
			b[i][j]=a[i][val];
			val++;
		}
	}
	
	cout<<"Output: "<<endl;
	for (int i=0;i<n;i++){
		for (int j=0;j<m;j++)
		    cout<<b[i][j]<<" ";
		cout<<endl;
	}
	
	return 0;
}
