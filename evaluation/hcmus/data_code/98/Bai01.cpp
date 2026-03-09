#include <iostream>
using namespace std;

#define MAX 100

void nhapMaTran(int a[][MAX], int &n)
{
    cin >> n;
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            cin >> a[i][j];
        }
    }
}

bool kiemTraDoiXungQuaDuongCheoChinh(int a[][MAX], int n)
{
    for (int i = 0; i < n; i++)
    {
        if (a[i][i] != a[n - i - 1][n - i - 1])
            return false;
    }
    return true;
}

bool kiemTraDoiXungQuaDuongCheoPhu(int a[][MAX], int n)
{
    for (int i = 0; i < n; i++)
    {
        if (a[i][n - i - 1] != a[n - i - 1][i])
            return false;
    }
    return true;
}

int main()
{
    int a[MAX][MAX];
    int n;
    nhapMaTran(a, n);
    if(kiemTraDoiXungQuaDuongCheoChinh(a, n) == true || kiemTraDoiXungQuaDuongCheoPhu(a, n) == true)
        cout << "True" << endl;
    else
        cout << "False" << endl;
    return 0;
}