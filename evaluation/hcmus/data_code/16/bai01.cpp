#include <iostream>
#include <fstream>
using namespace std;
const int SIZE = 10050;

bool checkExist(int arr[], int n, int k)
{
    for (int i = 0; i < n; ++i)
        if (k == arr[i]) return true;
    return false;
}

int makeOrderofDisks(int disk[], int num, int lis[], int changes)
{
    int k = changes - 1;
    for (int i = 0; i < changes; ++i)
    {
        disk[i] = lis[k];
        k--;
    }

    k = 1;
    for (int i = changes; i < num; ++i)
    {
        while (checkExist(lis, changes, k))
        {
            k++;
        }

        {
            disk[i] = k;
            k++;
        }
    }
}

int main()
{
    int num, changes, disk[SIZE], lis[SIZE];
    cout << "Input number of disks: ";
    cin >> num;
    cout << "Input number of changes: ";
    cin >> changes;
    cout << "The order of changes: ";
    for (int i = 0; i < changes; ++i)
        cin >> lis[i];

    makeOrderofDisks(disk, num, lis, changes);

    cout << "Disk stack: ";

    for (int i = 0; i < num - 1; ++i)
        cout << disk[i] << ' ';
    cout << disk[num - 1];


    return 0;
}

