#include<iostream>
using namespace std;

#define MAX 100

void getarr(int a[MAX],int &n)
{
    for(int i = 0; i < n; i++)
    {
        cin >> a[i];
    }
}

void printarr(int a[MAX],int &n)
{
    for(int i = 0; i < n; i++)
    {
        cout << a[i] << endl;
    }
}

void chenDauArr(int a[MAX],int &n)
{

}

int main()
{
    int arr[MAX], n;
    cout << "Input number of disks:";
    cin >> n;
}
