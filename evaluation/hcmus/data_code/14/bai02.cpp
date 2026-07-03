#include<iostream>
using namespace std;
const int Max = 100;

void exchange(int &a, int &b)
{
	int tempt = a;
	a = b;
	b = tempt;
}

void createMatrix(int a[][Max], int m, int n)
{
	int v1 = 0, v2 = n - 1;
	for (int i = 0; i < m; i++)
	{
		while (v1 < v2)
		{
			exchange(a[i][v1], a[i][v2]);
			v1 ++;
			v2 --;
		}
		v1 = 0; 
		v2 = n - 1;
	}
}

int main()
{
	int a[Max][Max];
	int n, m;
	cout<<"Input dim: ";
	cin>> m>> n;
 	cout<<"Input Arr: ";
 	for (int i = 0; i < m; i++)
 		for (int j = 0; j < n; j++) cin>> a[i][j];
 	createMatrix(a, m , n);
	cout<<"Output: "<<endl;
	for (int i = 0; i < m; i++)
	{
 		for (int j = 0; j < n; j++) cout<< a[i][j] <<" ";
		cout<<endl;
	}
	return 0;
}	
