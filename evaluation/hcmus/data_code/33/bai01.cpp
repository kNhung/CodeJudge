#include<iostream>
#include<cmath>
#include<cstring>
using namespace std;
void Nhap(int a[],int n)
{
	for(int i=0; i<n;i++)
	{
		a[i]=i+1;
	}
}
void Xuat(int a[],int n)
{
	for(int i=0;i<n;i++)
	{
		cout<<a[i]<<" ";
	}
}
void Them(int a[],int &n,int vt,int gt)
{
	for(int i=n;i>=vt;i--)
	{
		a[i+1]=a[i];
	}
	a[vt]=gt;
	n++;
}
void Xoa(int a[],int&n,int vt)
{
	
	for(int i=vt+1;i<n;i++)
	{
		a[i-1]=a[i];
	}
	n--;
	
}
void XuLi(int a[],int &n,int laydia)
{
	int tam = laydia;
	Them(a,n,0,tam);
	Xoa(a,n,tam);
	
}
int main()
{
	int a[10000];
	int n;
	cout<<"Input number of disks: ";
	cin>>n;
	Nhap(a,n);
	int lay;
	cout<<"\nInput number of changes: ";
	cin>>lay;
	for(int i=0;i<lay;i++)
	{
		int lay;
		cout<<"\nThe order of changes: "<<endl;
		cin>>lay;
		XuLi(a,n,lay);
	}
	Xuat(a,n);
	
}
