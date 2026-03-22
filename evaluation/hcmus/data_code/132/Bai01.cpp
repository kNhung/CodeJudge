#include <iostream>
#include <cmath>
#include <cstring>
using namespace std;

void input2D_Array(int a[][10],int n)
{
    n = sqrt(n);
    for(int i = 0;i < n;i++)
        for(int j = 0;j < n ;j++)
            cin >> a[i][j];
}

void output2D_Array(int a[][10],int n)
{
    n = sqrt(n);
    for(int i = 0;i <= n;i++)
        for(int j = 0;j < n;j++)
            cout << a[i][j];
}

bool check_Diagonal(int a[][10],int n)
{
    n = sqrt(n);
    int tmp1[500],tmp2[500],t1(0),t2(0);
    for(int i = 0;i < n - 1;i++)
        for(int j = 0;j < n - i - 1;j++)
        {
            tmp1[t1] = a[i][j];
            t1++;
        }
    for(int i = n - 1;i > 0 ;i--)
        for(int j = n - i - 1;j > 0 ;j--)
        {
            tmp2[t2] = a[i][j];
            t2++;
        }
    for(int i = 0;i <= t1;i++)
    {
        if(tmp1[i] != tmp2[i]) return 0;
    }
    return 1;
}

bool check_Sub_Diagonal(int a[][10],int n)
{
    n = sqrt(n);
    for(int i = n - 1;i > 0;i--)
        for(int j = n - 1;j > 0;j--)
        {
            if(i == j && i + j == n - 1) break;
            if(i + j != n - 1)
            {
                if(a[n - i][n - j] != a[i][j]) return 0;
            }
            else continue;
        }
    return 1;
}

int main()
{
    int a[10][10],n;
    cin >> n;
    input2D_Array(a,n);
    if(check_Diagonal(a,n) || check_Sub_Diagonal(a,n)) cout << "True";
    else cout << "False";
    return 0;
}
