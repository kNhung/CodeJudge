#include <iostream>
#include <cstring>
#include <cmath>

using namespace std;
#define MAX 100

void input(int a[][MAX], int &n)
{
    cin >> n;
    n = sqrt(n);
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            cin >> a[i][j];
        }
    }
}

void print(int a[][MAX], int n)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            cout << a[i][j] << " ";
        }
        cout << endl;
    }
}

bool check1(int a[][MAX], int n)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            if (a[i][j] != a[j][i])
            {
                return false;
            }
        }
    }
    return true;
}

bool check2(int a[][MAX], int n)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            if (a[i][j] != a[n - j - 1][n - i - 1])
            {
                return false;
            }
        }
    }
    return true;
}

bool check(int a[][MAX], int n)
{
    return (check1(a, n) || check2(a, n));
}

int main()
{
    int matrix[MAX][MAX];
    int n;

    input(matrix, n);
    print(matrix, n);

    if (check(matrix, n))
        cout << "True";
    else
        cout << "False";

    return 0;
}