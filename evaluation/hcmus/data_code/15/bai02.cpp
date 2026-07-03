#include <iostream>
#include <cstring>
#include <fstream>

using namespace std;

void Swap(int &a, int &b);

int main()
{

    int n, m;
    cout << "Input dim: ";
    cin >> n >> m;

    cout << "Input Arr: ";
    int arr[n][m];
    for(int i = 0; i < n; i++)
        for(int j = 0; j < m; j++)
            cin >> arr[i][j];

    for(int i = 0; i < n; i++)
        for(int j = 0; j < m / 2; j++)
            Swap(arr[i][j], arr[i][m - 1 - j]);

    cout << "Output: \n";

    for(int i = 0; i < n; i++)
    {
        for(int j = 0; j < m; j++)
            cout << arr[i][j] << " ";
        cout << "\n";
    }

    return 0;

}

void Swap(int &a, int &b)
{
    int temp = a;
    a = b;
    b = temp;
}
