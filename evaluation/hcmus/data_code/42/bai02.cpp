#include <iostream>
#include <cmath>
#include <cstring>
#include <string>
using namespace std;

void hoanVi(int &a, int &b){
    int temp = a;
    a = b;
    b = temp;
}

void maTranDoiXung(int a[][100], int n, int m){
    for (int i = 0; i < n; i++){
        for (int j = 0; j < m/2; j++){
            hoanVi(a[i][j],a[i][m-j-1]);
        }
    }
}

int main(){

    int n,m,a[100][100];
    cout << "Input dim: ";
    cin >> n >> m;
    cout << "Input Arr: ";
    for (int i = 0; i < n; i++){
        for (int j = 0; j < m; j++){
            cin >> a[i][j];
        }
    }
    maTranDoiXung(a,n,m);
    cout << "Output: " << endl;
    for (int i = 0; i < n; i++){
        for (int j = 0; j < m; j++){
            cout << a[i][j] << " ";
        }
        cout << endl;
    }

    return 0;
}
