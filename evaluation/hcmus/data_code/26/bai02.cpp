#include <iostream>

using namespace std;

void Input(int a[][10], int n, int m)
{
	for ( int i=0 ; i<=n-1 ; i++)
	{
		for ( int j=0 ; j<=m-1 ; j++)
		{
			cin >> a[i][j];
		}
	}
}

void Convert(int a[][10],int b[][10], int n, int m)
{
	for (int i=0;i<=n-1;i++)
	{
		for (int j=0;j<=m-1;j++)
		{
			b[i][m-1-j]=a[i][j];
		}
	}
}

void Output(int b[][10],int n, int m)
{
	for ( int i=0 ; i<=n-1 ; i++)
	{
		for ( int j=0 ; j<=m-1 ; j++)
		{
			cout << b[i][j]<< " ";
		}
		cout << endl;
	}
}
int main()
{
	int a[10][10];
	int b[10][10];
	int n,m;
	cout << "Input dim: ";
	cin >> n >> m;
	cout << "Input Arr: ";
	Input(a,n,m);
	Convert(a,b,n,m);
	cout << "Output: "<< endl;
	Output(b,n,m);
	return 0;
}
