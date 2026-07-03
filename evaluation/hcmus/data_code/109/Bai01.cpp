#include <iostream>
#include <cmath>

bool checkSymmetric(int a[], int n)
{
    int m = sqrt(n);
    int b[m][m];

    int k = 0;
    for (int i = 0; i < m; i++)
    {
        for (int j = 0; j < m; j++)
        {
            b[i][j] = a[k];
            k++;
        }
    }

    bool flag1 = true;
    bool flag2 = true;
    for (int i = 0; i < m; i++)
    {
        for (int j = 0; j < m; j++)
        {
            if (b[i][j] != b[j][i])
            {
                flag1 = false;
                break;
            }
        }
    }

    for (int i = 0; i < m; i++)
    {
        for (int j = 0; j < m; j++)
        {
            if (j != m - i - 1)
            {
                if (b[i][j] != b[m - j - 1][m - i - 1])
                {
                    flag2 = false;
                    break;
                }
            }
        }
    }

    return (flag1 || flag2);
}

int main()
{
    int n = 9;
    int a[] = {1,2,3,4,5,2,7,4,1};

    if (checkSymmetric(a, n) == true)
        std::cout << "true";
    else
        std::cout << "false";
    return 0;
}