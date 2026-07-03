/*
Ho ten: Le Nguyen Nhat Truong
Lop: 23CLC02
MSSV: 23127136

Bai 2 - De thi giua ki (thuc hanh)
Chuong trinh: Kiem tra so Automorphic

Input: so nguyen duong n
Output: 1 neu n la so automorphic, 0 neu nguoc lai #-1 neu input khong thoa
*/

#include <iostream>
#include <cmath>

using namespace std;

int ktraAutomorphic(int a);

int main() {
    int soKtra;
    cin >> soKtra;

    cout << ktraAutomorphic(soKtra);

    return 0;
}

int ktraAutomorphic(int a) {
    if (a <= 0) return -1;

    for (int i = a * a; i > 0; i /= 10) {
        if (i % 10 != a % 10) return 0;
        if (a < 10) {
            return (i % 10 == a) * 1;
        }
        a /= 10;
    }
}
