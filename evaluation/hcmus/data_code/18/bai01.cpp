#include <iostream>

using namespace std;

const int N = 10000;

int main()
{
    int n, a[N], b[N];
    cout << "Input number of disks: ";
    cin >> n;

    int m;
    cout << "Input number of changes: ";
    cin >> m;

    cout << "The order of changes: ";
    for (int i = 0 ; i < m; i++)
        cin >> a[i];

    for (int i = 0; i < n; i++)
        b[i] = i + 1;

    for (int i = 0; i < m; i++)
    {
        for (int j = a[i] - 2 + i; j >= 0; j--)
            b[j + 1] = b[j];
        b[0] = a[i];


    }

    cout << "Disk stack: ";
    for (int i = 0; i < n; i++)
        cout << b[i] << " ";

    return 0;


}
