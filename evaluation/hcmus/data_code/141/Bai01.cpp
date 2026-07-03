// Cho ma trận n x n. Viết hàm kiểm tra mảng có đối xứng qua đường chéo hay không? Kiểm tra
// đối xứng qua đường chéo chính hoặc đường chéo phụ. Nếu thoả mãn một trong hai tính chất
// thì trả về True, không trả về False
#include <iostream>
#include <string.h>
#include <cmath>
using namespace std;


//nhap mang
void InputArr(int a[][100], int& n ){
    for(int i=0;i<n;i++){
        for(int j = 0;j < n ; j ++){
           cin>>a[i][j];
        }
    }
}
//kiem tra cos doi xung qua duong cheo chinh
int Check_Arr1(int a[][100],int n  ){
    for(int i = 0; i < n;i++ ){
        for(int j = 0; j < n ; j ++){
            if(a[i][j] != a[j][i]){
                return 0;
            }
        }
    }
    return 1;
}
// kiem tra co doi xung qua duong cheo phu
int Check_Arr2(int a[][100],int n  ){
    for(int i = 0; i < n;i++ ){
        for(int j = 0; j < n ; j ++){
            if(a[i][j] != a[n-1-j][n-i-1]){
                return 0;
            }
        }
    }
    return 1;
}

int main (){
    int a[100][100];
    int n;
    cin>>n;

    InputArr(a,n);

    if(Check_Arr1(a,n) || Check_Arr2(a,n)){
        cout<<"True";
    }
    else 
        cout<<"False";

    return 0;
}
