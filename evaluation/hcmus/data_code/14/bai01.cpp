#include<iostream>
const int Max = 100;
using namespace std;
void arrangeDisk(int a[], int n, int b)
{
	int pos;
	for (int i = 0; i < n; i ++) 
		if (a[i] == b) 
		{
			pos = i;
			break;
		}
	for (int i = pos; i > 0; i --)
	{
		a[i] = a[i - 1];
	}
	a[0] = b;
}
int main()
{
	int a[Max], b[Max], n, c;
	cout<<"Input number of disks: ";
	cin>> n;
	for (int i = 0; i < n; i++) a[i] = i + 1;
	
	cout<<"Input number of changes: ";
	cin>> c;
	
	cout<<"The order of changes: ";
	for (int i = 0; i < c; i++) cin>> b[i];
	for (int i = 0; i < c; i++) arrangeDisk(a, n, b[i]);
	
	cout<<"Disk stack: ";
	for (int i = 0; i < n; i ++) cout<<a[i] <<" ";
	return 0;
}
