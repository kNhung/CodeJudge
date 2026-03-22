#include <iostream>
#include <cmath>
using namespace std;

const int MAX = 100;

bool is_symmetric(int a[][MAX], int n)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            if (i != j)
            {
                if (a[i][j] != a[j][i])
                {
                    return false;
                }
            }
            else if (j != n - i - 1)
            {
                if (a[i][j] != a[n - 1 - j][n - 1 - i])
                {
                    return false;
                }
            }
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
    {
        for (int j = 0; j < n; j++)
        {
            cin >> a[i][j];
        }
    }

    if (is_symmetric(a, n))
    {
        cout << "True";
    }
    else
    {
        cout << "False";
    }

    return 0;
}