#include <iostream>

using namespace std;

void input(int a[][100], int& n, int& m){
    for (int i = 0; i < n; i++){
        for( int j = 0; j < m; j++){
            cout << "Input Arr: ";
            cin >> a[i][j] ;
        }
    }
}

void output(int a[][100], int n, int m){
    for (int i = 0; i < n; i++){
        for( int j = 0; j < m; j++){
            int b[i][100];
            b[i][j] = a[i][m - j - 1];
            cout << b[i][j] << " ";
        }
        cout << endl;
    }
}

int main(){
    int n, m;
    cout << "Inout dim: ";
    cin >> n >> m;
    int a[n][100];
    input (a, n, m);
    output(a, n ,m);
    return 0;
}
