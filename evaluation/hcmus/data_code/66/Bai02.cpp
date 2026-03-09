#include<iostream>
using namespace std;

//Ham kiem tra so automorphic//
bool soAutomorphic (int n) {
    int binh_phuong = n * n;
    while ( n > 0) {
        if ( n % 10 != binh_phuong % 10)
            return false;
        n /= 10;
        binh_phuong /= 10;
    }
    return true;
}


int main()
{
    int n;
    //dung vong lap neu n khong phai la so nguyen duong thi nhap toi khi thoa man//
    do{
        cin >> n;
        if ( n <= 0);
    } while (n <= 0);
    //Goi ham de kiem tra so automorphic va xuat ra man hinh//
    cout << soAutomorphic(n);
    
    return 0;

}


