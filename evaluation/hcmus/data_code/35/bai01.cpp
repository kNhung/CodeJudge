#include <iostream>
using namespace std ;
int main()
{
    int disks[10000],numdisk=1;
    int n,k , noofdisk[10000];
    do{cout << "Input number of disks: " ;
    cin >> n ;}
    while(n<=0 || n>10000);
    for (int i=0 ; i<n ; i++)
    {
        disks[i]=numdisk;
        numdisk++;
    }
    do{cout << "Input number of changes: " ;
    cin >> k ;}
    while(k<=0 || k>n);
    cout << "The order of changes: " ;
    for(int i=0 ; i<k ; i++)
    {
        do{cin >> noofdisk[i];}
        while (noofdisk[i]<=0) ;
    }
    for(int i=0,j=0 ; i<n ; i++)
    {
        if(disks[i]==noofdisk[j])
        {
            for(int m=i; m>0 ; m--)
                disks[m]=disks[m-1];
            disks[0]=noofdisk[j];
            j++;
            i=0;
        }
    }
    cout << "Disk stack: " ;
    for (int i=0 ; i<n ; i++)
        cout << disks[i] << " " ;
    return 0;

}
