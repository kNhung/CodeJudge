#include<iostream>
using namespace std;
#define MAX 100

void NHAP_MANG(int a[][MAX], int& n){
    cout << "Nhap vao n: ";
    cin >> n;
    for(int i = 0; i < n; i++){
        for(int j = 0; j < n; j++){
            cout << "a[" << i << "][" << j << "] = ";
            cin >> a[i][j];
        }
    }
}
void XUAT_MANG(int a[][MAX], int& n){
    for(int i = 0; i < n; i++){
        for(int j = 0; j < n; j++){
            cout << a[i][j] << " ";
        }
        cout << endl;
    }
}
int XET(int a[][MAX], int n){
    for(int i = 0; i < n - 1; i++){
        for(int j = 0; j < n - 1; j++){
            if((a[i + 1][j] == a[i][j + 1]) || (a[i][j] == a[n-1][n-1]) ){
                return 1;
            }
        }
    }
    return 0;
}
int main(){
    int a[MAX][MAX];
    int n;
    NHAP_MANG(a, n);
    XUAT_MANG(a, n);
    if(XET(a, n) == 1){
        cout << "True" << endl;
    }
    else{
        cout << "False" << endl;
    }
    return 0;
}
