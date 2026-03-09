#include <iostream>

using namespace std;

void input(int a[][100], int& n){
    cout << "Nhap phan tu cua mang:\n";
    for(int i = 0; i < n; i++)
        for(int j = 0; j < n; j++)
            cin >> a[i][j];
}

void print(int a[][100], int& n){
    for(int i = 0; i < n; i++){
        for(int j = 0; j < n; j++)
            cout << a[i][j] << '\t';
        cout << endl;
    }
}    

bool kiemtradoixung(int a[][100], int& n){
    for(int i = 0; i < n; i++){
        for(int j = 0; j < n; j++){
            if(i != j && (a[0][0] != a[n-1][n-1] ||a[i][j] != a[i + 1][j] || a[i][j + 1] != a[i][j] || a[i][j] != a[j][i]))
                return false;
        }
    }
    return true;
}

int main(){
    int a[100][100];
    int n;
    cout << "Nhap do dai canh: ";
    cin >> n;
    input(a, n);
    print(a, n);
    cout << kiemtradoixung(a, n);
}