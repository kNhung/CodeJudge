#include <iostream>

using namespace std;

int main()
{
    int n;
    int a[10001], b[10001];
    int changes;
    cout << "Input number of disks: ";
    cin >> n;
    cout << "Input number of changes: ";
    cin >> changes;
    int change[1000];
    for (int i = 1; i <= n; i++){
        a[i] = i;
    }
    cout << "The order of changes: ";
    for (int i = 1; i <= changes; i++){
        cin >> change[i];
    }
    for (int i = 1; i <= changes; i++)
    {
        b[1] = change[i];
        for (int j = i+1; j <= n; j++)
        {
            if (a[j-1] == change[i]){
                while (j <= n)
                {
                    b[j] = a[j];
                    j++;
                }
            }
            else
                b[j] = a[j-1];

        }
        for (int k = 0; k < n; k++)
        {
            a[k] = b[k];
        }
    }
    cout << "Disk stack: ";
    for (int i = 1;i <= n; i++)
    {
        cout << b[i] << ' ';
    }
    return 0;
}
