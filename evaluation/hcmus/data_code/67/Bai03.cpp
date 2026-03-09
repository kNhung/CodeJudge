// Kiem tra so doi xung

#include <iostream>

using namespace std;

int main(){
    int m, nghin, tram, chuc, dvi; 
        cout << "Nhap so nguyen duong m (1000 <= m <= 9999): ";
        cin >> m;
    if(m < 1000 || m > 9999)
        cout << "Nhap sai";
    else{
        dvi = m % 10;
        chuc = (m % 100 - dvi)/10;
        tram = (m % 1000 - chuc)/100;
        nghin = (m % 10000 - tram)/1000;
        if((dvi * 10 + chuc) == (nghin * 10 + tram))
            cout << m << " (Xoa 0 chu so)";
    }
}