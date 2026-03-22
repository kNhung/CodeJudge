#include <iostream>
#include <cmath>
#include<string>
#include<cstring>
#include <cstdlib>
#include <stdlib.h>

using namespace std;
#define row 100
#define col 100
#define max 100

void nhapmang(int arr[][col], int& n, int& m)
{
    cout << "Nhap so dong va cot: ";
    cin >> n >> m;
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < m; j++)
        {
           cin>> arr[i][j] ;
        }
    }
}
void xuatmang(int arr[][col], int n, int m)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < m; j++)
        {
            cout << arr[i][j] << " ";
        }
        cout << endl;
    }
}

void mang_doi_xung(int arr[][col],int a[][col],int &n,int&m)
{
    int k= m-1;
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < m; j++)
        {
          a[i][k]=arr[i][j];
          k--;
        }
        k=m-1;
    }
}
int main()
{
   int arr[row][col], a[row][col],n,m;
   nhapmang(arr,n,m);
   mang_doi_xung(arr,a,n,m);
   xuatmang(a,n,m);
   return 0;
}
