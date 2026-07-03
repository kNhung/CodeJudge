//23127120 Tran Danh Thien
#include <iostream>
#include <cstring>
#include <cmath>

using namespace std;

bool isdx(int a[][1000], int m){
    int cnt = 0;
    int dem = 0;
    int n = 0;
    while (n*n != m)
    {
        n++;
    }
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            if ((i + j + 1) != n)
            {
                if (a[i][j] == a[n - j - 1][n - i - 1])
                {
                    cnt++;
                }
            } 
        }
    }
    if (cnt == (n*n - n)) return true;
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            if ( i != j )
            {
                if (a[i][j] == a[j][i])
                {
                    dem++;
                }
            }
        }
    }
    if (dem == (n*n - n)) return true;
    if (dem != (n*n - n))
    {
        if (cnt != (n*n - n)) return false;
    }
}

int main(){
    
}