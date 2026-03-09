#include <iostream>
#include <cmath>
#include <cstring>

bool checkMirrorDiagonal(int arr[][100], int& n)
{
    std::cin >> n;

    bool checkMirrorRight{1};
    bool checkMirrorLeft{1};

    n = sqrt(n);

    for (int i{0}; i < n; ++i)
    {
        for (int j{0}; j < n - 1; ++j)
        {
            if (arr[i][j] != arr[n - i - 1][n - j - 1])
                checkMirrorLeft = 0;
        }
        --n;
    }

    for (int i{0}; i < n; ++i)
    {
        for (int j{i + 1}; j < n; ++j)
        {
            if (arr[i][j] != arr[j][i])
                checkMirrorRight = 0;
        }
    }

    if (checkMirrorLeft || checkMirrorRight)
        return true;
    else
        return false;
}

int main()
{
    return 0;
}
