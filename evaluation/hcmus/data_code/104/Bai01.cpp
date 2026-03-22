#include <iostream>
#include <cstring>
#include <cmath>
using namespace std;

void setA(int a[][10], int& n){
    cin >> n;
    n = sqrt(n);

    for(int i = 0; i < n; i++){
        for(int j = 0; j < n; j++){
            cin >> a[i][j];
        }
    }
}

bool checkDoiXung(int a[][10], int n){
    for(int i = 0; i < n; i++){
        for(int j = 0; j < n; j++){
            if(a[i][j] != a[n - 1 - j][n - 1 - i]){
                return false;
            }
        }
    }

    return true;
}

int main(){
    int a[10][10];
    int n;
    setA(a, n);
    cout << checkDoiXung(a, n);

    return 0;
}