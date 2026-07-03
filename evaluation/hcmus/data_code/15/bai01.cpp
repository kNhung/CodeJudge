#include <iostream>
#include <cstring>
#include <fstream>

using namespace std;

int main()
{
    int num_disk, num_change;

    cout << "Input number of disks: ";
    cin >> num_disk;

    cout << "Input number of changes: ";
    cin >> num_change;

    int disk[num_disk];
    for(int i = 0; i < num_disk; i++)
        disk[i] = i + 1;

    cout << "The order of changes: ";
    for(int k = 0; k < num_change; k++)
    {
        int disk_listen;
        cin >> disk_listen;
        for(int i = 0; i < num_disk; i++)
            if(disk[i] == disk_listen)
            {
                for(int j = i; j >= 1; j--)
                    disk[j] = disk[j - 1];
                disk[0] = disk_listen;
            }
    }

    cout << "Disk stack: ";
    for(int i = 0; i < num_disk; i++) cout << disk[i] << " ";

    return 0;

}
