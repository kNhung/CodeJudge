#include <iostream>
#include <cmath>

using namespace std;

void inputArray(int a[][10], int &n)
{
    int m;
    cout <<"Nhap so phan tu co trong ma tran: ";
    cin >>m;

    n = sqrt(m);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
        {
            cout <<"Nhap a["<<i<<"]["<<j<<"]: ";
            cin >>a[i][j];
        }
}

int ktraDgCheoPhu(int a[][10], int n)
{
    int b[100], c[100];
    int nb = 0, nc = 0;

    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
        {
            if (i + j != n - 1)
            {
                if (i >= j )
                {
                    b[nb] = a[i][j];
                    nb += 1;
                }
                else if (j >= i)
                {
                    c[nc] = a[i][j];
                    nc += 1;
                }
            }
            
        }

    int l = 0, r = nb - 1;
    for (int i = 0; i < nb; i++)
    {
        if (b[l] != c[r]) return 1;
        l++ ; r--;
    }
    return 0;  
}

int ktraDgCheoChinh(int a[][10], int n)
{
    int b[100], c[100];
    int nb = 0, nc = 0;

    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
        {
            if (i != j)
            {
                if (i > j )
                {
                    b[nb] = a[i][j];
                    nb += 1;
                }
                else if (j > i)
                {
                    c[nc] = a[i][j];
                    nc += 1;
                }
            }
            
        }

    int l = 0, r = nb - 1;
    for (int i = 0; i < nb; i++)
    {
        if (b[l] != c[r]) return 1;
        l++ ; r--;
    }
    return 0;  
}


int main()
{
    int a[10][10];
    int n;

    inputArray(a, n);
    if (ktraDgCheoPhu(a, n) || ktraDgCheoChinh(a, n))
        cout <<"True";
    else 
        cout <<"False";
    return 0;
}