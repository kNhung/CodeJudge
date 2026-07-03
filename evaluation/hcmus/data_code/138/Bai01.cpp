#include <iostream>
#include <cmath>
using namespace std;

const int MAX = 100;

void setArr (int a[][MAX], int& n){
    cin >> n;
    n = sqrt(n);
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            cin >> a[i][j];
}

bool ktraDoiXungQuaDuongCheoChinh (int a[][MAX], int n){
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            if (i == j)
                continue;
            else
                if (a[i][j] == a[j][i])
                    continue;
                else{
                    return false;
                }
    return true;
}

bool ktraDoiXungQuaDuongCheoPhu (int a[][MAX], int n){
    int temp[MAX][MAX];
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            temp[i][j] = a[i][n - 1 - j];
        
    ktraDoiXungQuaDuongCheoChinh(temp, n);
    return true;
}

int main(){
    int a[MAX][MAX], n;
    setArr(a, n);
    bool chinh = ktraDoiXungQuaDuongCheoChinh(a, n);
    bool phu = ktraDoiXungQuaDuongCheoPhu(a, n);
    bool flag = chinh || phu;
    if (flag == true)
        cout << "True";
    else
        cout << "False";


    return 0;
}