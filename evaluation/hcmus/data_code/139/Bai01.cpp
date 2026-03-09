/*
    Ta Xuan Truong _ 23127506
*/

#include <iostream>
#include <cstring>

using namespace std;

const int MAXNUM = 1000;

void inputArr(int a[MAXNUM][MAXNUM], int &n, int &m)
{
    cin >> m >> n;
    for (int i = 0; i < m; i++)
        for (int j = 0; j < n; j++)
            cin >> a[i][j];
}

bool checkDoiXung(const int a[MAXNUM][MAXNUM],const int m,const int n)
{
    int temp = n;
    bool check = 1;
    for (int i = 0, jj = n - 1; i < m - 1; i++, jj--) {
        for (int j = 0 , ii = m -1; j < temp - 1; j++, ii --)
            if (a[i][j] != a[ii][jj]){
                check = 0;
                break;
            }
    }
    if (check == 1)
        return 1;
    for (int i = 0, jj = 0; i < m - 1; i++, jj++) {
        for (int j = n - 1 , ii = m -1 ; j >= 0; j--, ii --)
            if (a[i][j] != a[ii][jj]){
                return 0;
            }
    }
    return 1;
}

int main()
{
    int list[MAXNUM][MAXNUM], row, col;
    inputArr(list, row, col);
    if (checkDoiXung(list, row, col))
        cout << "True";
    else
        cout << "False";
    
    return 0;
}
