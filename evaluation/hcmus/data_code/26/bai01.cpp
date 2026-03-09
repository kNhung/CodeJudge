#include <iostream>

using namespace std;
void Input(int a[],int c[],int n)
{
	int val=1;
	for (int i=0;i<=n-1;i++){
		a[i]=val++;
		c[i]=a[i];
	}
}
void SelectDisk(int a[],int c[], int n, int m, int &b)
{
	while (m>=1)
	{
		m--;
		cin >> b;
		for (int i=0;i<=n-1;i++)
		{
			if (a[i]=b)
			a[0]=a[i];
			for (int j=1;j<=n-1;j++)
			{
				if (a[j-1]!=b)
				c[j]=a[j-1];
			}
		}
	}
}
int main()
{
	int a[10];
	int c[10];
	int n,ch,b;
	cout << "Input number of disks: ";
	cin >> n;
	cout << "Input number of changes: ";
	cin >> ch;
	cout << "The order of changes: ";
	SelectDisk(a,c,n,ch,b);
	cout << "Disk stack: ";
	for (int i=0;i<=n-1;i++){
		cout << c[i]<< " ";
	}
	return 0;
}
