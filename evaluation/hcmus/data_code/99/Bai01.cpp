#include <iostream>
#include <cmath>
using namespace std;
#define MAXL 100
#define MAXC 100

void inputMatrix(int m[][MAXC], int& n, int& l, int& c)
{
    cin >> n;
    l = sqrt(n);
    c = sqrt(n);
    for (int i = 0; i < l; i++)
    {
        for (int j = 0; j < c; j++)
        {
            cin >> m[i][j];
        }
    }
}

bool isSymmetric(int matrix[][MAXC], int n) 
{
    for (int i = 0; i < n; i++)
    {
        for (int j = i + 1; j < n; j++) 
        {
            if (matrix[i][j] != matrix[j][i]) 
            {
                break;
            }
            if (j == n - 1)
            {
                return true;
            }
        }
    }
    for (int i = 0; i < n; i++) 
    {
        if (matrix[i][i] != matrix[n - 1 - i][n - 1 - i]) 
        {
            break;
        }
        if (i == n - 1) 
        {
            return true;
        }
    }
    return false;
}

int main() 
{
    int l, c, n;
    int matrix[MAXL][MAXC];

    inputMatrix(matrix, n, l, c);
    if (isSymmetric(matrix, l))
    {
        cout << "True" << endl;
    }
    else
    {
        cout << "False" << endl;
    }

    return 0;
}
