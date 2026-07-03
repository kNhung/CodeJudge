#include<iostream>
using namespace std;

#define MAXCol 100
#define MAXRow 100

void getArr(int arr[][MAXCol], int &n, int &m)
{
    cout << "Input Arr:";
    for(int i = 0; i < n; i++)
    {
        for(int j = 0; j < m; j++)
        {
            cin >> arr[i][j];
        }
    }
}

void printArr(int a[][MAXCol], int n, int m)
{
    for(int i = 0; i < n; i++)
    {
        for(int j = 0; j < m; j++)
        {
            cout << a[i][j] << "\t";
        }
        cout << endl;
    }
}

void mang_doi_xung(int a[][MAXCol], int b[][MAXCol], int &n, int &m)
{
    int k = m - 1;
    for(int i = 0; i < n; i++)
    {
        for(int j = 0; j < m; j++)
        {
            b[i][k] = a[i][j];
            k--;
        }
        k = m - 1;
    }
}


int main()
{
    int a[MAXRow][MAXCol], b[MAXRow][MAXCol], n, m;
    cout << "Input dim:";
    cin >> n >> m;
    getArr(a, n, m);
    mang_doi_xung(a, b, n, m);
    cout << "Output:" << endl;
    printArr(b, n, m);
}

