#include <iostream>
#include <cmath>
using namespace std;

#define MAX 100

bool DoiXungCheoChinh(int a[MAX][MAX], int n){
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            if (a[i][j] != a[j][i])
                return false;
    return true;
}

bool DoiXungCheoPhu(int a[MAX][MAX], int n){
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++){
            if ((i + j != n - 1) && (a[i][j] != a[n - j - 1][n - i - 1]))
                return false;
        }
    return true;
}

bool KiemTraDoiXung(int a[MAX][MAX], int n){
    if (DoiXungCheoChinh(a, n) || DoiXungCheoPhu(a, n))
        return true;
    return false;
}

int main(){
    int n;
    cin >> n;
    n = trunc(sqrt(n));
    int a[MAX][MAX];
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            cin >> a[i][j];
    if (KiemTraDoiXung(a, n))
        cout << "TRUE";
    else
        cout << "FALSE";
    return 0;
}
