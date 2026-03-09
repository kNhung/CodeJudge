#include <iostream>
#include <cstring>
#include <cmath>

using namespace std;

#define MAX 100

bool checkSymmetricMainDig(int a[][MAX], int n)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            if (a[i][j] != a[j][i])
                return false;
        }
    }
    return true;
}

bool checkSymmetricDig(int a[][MAX], int n)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            if (a[i][j] != a[n - j - 1][n - i - 1])
                return false;
        }
    }
    return true;
}

int main()
{
    int n;
    int a[MAX][MAX];

    cin >> n;
    n = sqrt(n);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            cin >> a[i][j];

    if (checkSymmetricMainDig(a, n) || checkSymmetricDig(a, n))
        cout << "True" << endl;
    else
        cout << "False" << endl;
    return 0;
}