#include <iostream>
#include <cmath>

using namespace std;

#define MAXROW 16
#define MAXCOL 16

// ham nhap nhap kich thu0c ma tran va gia tri
void inputArray2d(int a[][MAXCOL], int &n){
    cout << "Nhap so phan tu cua ma tran(n x n): ";
    cin >> n;
    n = sqrt(n);
        for(int h = 0; h < n; h++){
            for(int c = 0; c < n; c++){
                cout << "a[" << h << "][" << c << "]= ";
                cin >> a[h][c];
            }
        }
    
}

int timDuongCheoChinh(int a[][MAXCOL], int n){
    int tmp = 1;
    for(int h = 0; h < n; h++){
        for(int c = h;  c < n; c++){
            if(a[h][c] != a[c][h]){
                tmp = 0;
                break;
            }
        }
    }
    return tmp;
}

int timDuongCheoPhai(int a[][MAXCOL], int n){
    int tmp = 1;
    for(int h = n-1; h >= 0; h--){
        int k = 0;
        for(int c = h;  c < n; c++){
            
            if(a[h][c] != a[c][k]){
                tmp = 0;
                break;
            }
        }
        k++;
    }
    return tmp;
    
}

void print(int a[][MAXCOL], int n){
   
    if(timDuongCheoChinh(a, n) == 1 || timDuongCheoPhai(a, n) == 1)
        cout << "True";
    else 
        cout << "False";
}

int main(){
    int n;
    int a[MAXROW][MAXCOL];
    inputArray2d(a, n);
    // print(a, n);
    return 0;
}