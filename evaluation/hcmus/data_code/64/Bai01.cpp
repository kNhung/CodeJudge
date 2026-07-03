/*
Ho ten: Le Nguyen Nhat Truong
Lop: 23CLC02
MSSV: 23127136

Bai 1 - De thi giua ki (thuc hanh)
Chuong trinh: Tinh tong cac so chan trong khoang tu a den b

Input: 2 so nguyen a b
Output: Tong cac so chan
*/

#include <iostream>

using namespace std;

int tongSoChan(int a, int b);

int main() {
    int a, b;
    cout << "Nhap a, b: ";
    cin >> a >> b;

    cout << tongSoChan(a, b);
    
    return 0;
}

int tongSoChan(int a, int b) {
    int result(0);

    if (a > b) return 0;
    else if (a == b) return (a % 2 == 0 ? a : 0);

    for (int i = a; i <= b; i++) {
        if (i % 2 == 0) result += i;
    }

    return result;
}
