/*
23CLC02 - 23127266 - NGUYEN ANH THU

Input:
Output:
*/
#include <iostream>
#include <cmath>

using namespace std;

const int MAX = 101;

bool doixung(int mang[MAX], int n)
{
    for (int i = 0; i * 2 < n; i++)
        if (mang[i] != mang[n - i - 1])
            return 0;
    return 1;
}

bool cheotrai1(int a[][MAX], int n)
{
    int b[MAX];

    for (int i = 0; i < n - 1; i++)
    {
        int dem = 0;
        for (int j = 1; j < n; j++)
        {
            b[dem++] = a[i][j];
            cout << b[dem - 1] << " ";
        }
        cout << "\n";
    }
    return 1;
}

bool xuli(int a[][MAX], int n)
{
    return cheotrai1(a, n);
    // if (cheotrai1(a) && cheotrai2(a) && cheophai1(a) && cheophai2(a))
    return 1;
    return 0;
}

int main()
{
    int n;
    int a[MAX][MAX];
    cin >> n;

    n = sqrt(n);
    // for (int i = 0; i < n; i++)
    //     for (int j = 0; j < n; i++)
    //         cin >> a[i][j];

    // if (xuli(a, n))
    //     cout << "True";
    // else
    //     cout << "False";

    return 0;
}