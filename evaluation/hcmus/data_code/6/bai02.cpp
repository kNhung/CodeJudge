#include <iostream>

using namespace std;
void revArr (int b[][100], int a[][100], int n, int m)
{
    for (int i = 0; i < n; i++)
    {
        int k = 0;
        for (int j = m-1; j >= 0; j--) {
            b[i][j] = a[i][k++];

        }
    }
}
int main()
{
    int a[100][100];
    int b[100][100];
    int n, m;
    cout << "Input dim: ";
    cin >> n >> m;
    cout << "Input Arr: ";
    for (int i = 0; i < n; i++)
    {
        for (int j=0; j < m; j++)
            cin >> a[i][j];
    }
    revArr(b,a,n,m);
    cout << "Output:" << endl;
    for (int i = 0; i < n; i++)
    {
        for (int j=0; j < m; j++)

            cout << b[i][j] << ' ';
        cout << endl;
    }

    return 0;
}
