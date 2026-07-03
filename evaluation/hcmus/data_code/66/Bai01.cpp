#include<iostream>
using namespace std;
int main()
{
    int a, b;
    cin >> a >> b;
    //khai bao tong = 0//
    int tong = 0;
    //dung vong lap de tinh tong cac so chan nam trong a va b//
    for (int i = a; i <= b; i++) {
        //Neu la so chan thi tong++//
        if(i % 2 == 0)
            tong += i;
    }
    //Xuat ket qua //
    cout << tong << endl;
    return 0;
}