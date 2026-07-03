#include <iostream>
#include <cmath>
#include<string>
#include<cstring>
#include <cstdlib>
#include <stdlib.h>
#define Max 10000
using namespace std;
void nhapmang(int arr[], int& n)
{
	for (int i = 0; i < n; i++)
	{
		cin >> arr[i];
	}
}
void xuatmang(int arr[], int n)
{
	for (int i = 0; i < n; i++)
	{
		cout << arr[i] << " ";
	}
}
void doidia(int arr[],int a[],int n,int x)
{

    for(int i=x-1;i>=1;i--)
    {
        arr[i]=arr[i-1];
    }
    arr[0]=a[0];
}

int main()
{
    int arr[Max];
    int a[Max];
    int n;//so dia
    cout << "nhap n: ";
	cin >> n;
    nhapmang(arr,n);
    int x;// so lan doi
    cin>>x;
    for(int i=0;i<x;i++)
    {
        cin>>a[i];
    }

    for(int i=0;i<x;i++)
    {
        for(int j=0;j<n;j++)
        {
            if(arr[j]==a[i])
            {
                doidia(arr,a,n,a[i]);
                xuatmang(arr,n);
                cout<<endl;
                break;
            }
        }
    }
    xuatmang(arr,n);

    return 0;
}

