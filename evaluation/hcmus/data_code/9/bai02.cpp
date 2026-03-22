#include <iostream>
#include <string>
#include <fstream>
using namespace std;
void sortMatrix(int a[][100], int m, int n){
    int mid = n / 2;
    for (int i = 0; i < m; i++){
        for (int j = 0; j < mid; j++){
            int temp = a[i][j];
            a[i][j] = a[i][n - j - 1];
            a[i][n - j - 1] = temp;
        }
    }
}
int main(){
    cout << "Input dim: ";
    int m, n;
    cin  >> m >> n;
    cout << "Input Arr: ";
    int a[100][100];
    for (int i = 0; i < m; i++){
        for (int j = 0; j < n; j++){
            cin >> a[i][j];
        }
    }
    cout << "Output: " << endl;
    sortMatrix(a, m, n);
    for (int i = 0; i < m; i++){
        for (int j = 0; j < n; j++){
            cout << a[i][j] << " ";
        }
        cout << endl;
    }
}
