#include <iostream>

using namespace std;

const int N = 10;

int main()
{
    int n, m, a[N][N];
    cout << "Input dim: ";
    cin >> n >> m;

    cout << "Input Arr: ";
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            cin >> a[i][j];

    if (m % 2 != 0)
    {
        for (int i = 0; i < n; i++)
            for (int j = 0; j < (m - 1)/2; j++)
            {

                int temp = a[i][j];
                a[i][j] = a[i][m - j - 1];
                a[i][m - j - 1] = temp;
            }
    }
    else {
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m/2; j++)
            {
                int temp = a[i][j];
                a[i][j] = a[i][m - j - 1];
                a[i][m - j - 1] = temp;
            }
    }

    cout << "Output: " << endl;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++)
            cout << a[i][j] << " ";
        cout << endl;
    }

    return 0;
}
