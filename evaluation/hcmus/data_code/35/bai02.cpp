#include <iostream>
using namespace std ;
void swapp (int &a,int &b)
{
    int tmp;
    tmp=a;
    a=b;
    b=tmp;
}
void change (int a[][100], int row, int col)
{
    for (int i=0 ; i<row ; i++)
    {
        int k=0;
        for (int j=0 ; j<col/2 ; j++)
        {
            swapp(a[i][j],a[i][col-1-k]);
            k++;
        }
    }
}
int main()
{
    int a[100][100];
    int row,col ;
    do{cout << "Input dim: " ; cin >> row >> col;}
    while (row<=0 || col <=0);
    cout << "Input Arr: " ;
    for (int i=0 ; i<row ; i++)
        for (int j=0 ; j<col ; j++)
            cin >> a[i][j] ;
    change (a,row,col) ;
    cout << "Output:\n" ;
    for (int i=0 ; i<row ; i++)
    {
         for (int j=0 ; j<col ; j++)
                cout << a[i][j] << "\t" ;
         cout << "\n" ;
    }
    return 0;
}
