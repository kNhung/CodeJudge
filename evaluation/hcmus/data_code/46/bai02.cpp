#include<iostream>
#include<cmath>

using namespace std;

int dao(int a, int b)
{
	int dc;
	dc = a; 
	a=b; 
	b=dc;
	
}

int main()
{
	int a[100][100];
	int b[100][100];
	int n;
	int m;
	int x;
	int y;
	int s;
	cout<<"\n nhap so dong:=";
	cin>>n;
	cout<<"\n nhap so cot:=";
	cin>>m;
	for(int i=0; i<n; i++){
		for(int j=0; j<m; j++)
		cin>>a[i][j];
	}
	x= (m+1)/2;
	
//	for(int i=0; i<n; i++){
//		y= m-1;
//		for(int j=0; j<= x;j++){
//			s = a[i][j];
//		//	a[i][j]= a[i][y];
		//	a[i][y] = s;
	//	cout<<s<<"\n";
	//	cout<<a[i][y];
//	dao(a[i][j],a[i][y]);
//		y=y-1;
 //       }
//	}
	for(int i=0; i<n; i++){
		y=m-1;
		for(int j=0; j<m; j++){
			//cout<<a[i][j]<<"\t";
			b[i][y]=a[i][j];
			y--;
		}
	}
		for(int i=0; i<n; i++){
		y=m-1;
		for(int j=0; j<m; j++){
		cout<<b[i][j]<<" ";
	}
	cout<<"\n";
	}
	return 0;
}

