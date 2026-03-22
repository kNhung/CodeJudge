// Kiem tra so automorphic

#include <iostream>
#include <cmath>

using namespace std;

bool ktra_automorphic(int& n){ 
    int binhphuong, soketthuc, dem=0, temp=n;

    binhphuong=pow(n,2);

    while(temp != 0){
        temp/=10;
        dem++;
    }
    int a= pow(10,dem);
        soketthuc= binhphuong % a;

    if(soketthuc==n)
        return 1;
    else
        return 0;
}

int main(){
    int n; 
        cout << "Nhap so tu nhien n (n>0): ";
        cin >> n;
    if(n<=0)
        cout << "Nhap sai";
    else{
        cout << ktra_automorphic(n);
    }
    return 0;
}