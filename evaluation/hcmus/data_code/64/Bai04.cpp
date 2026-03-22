/*
Ho ten: Le Nguyen Nhat Truong
Lop: 23CLC02
MSSV: 23127136

Bai 4 - De thi giua ki (thuc hanh)
Chuong trinh: kiem tra 2 so ban be 

Input: 2 so nguyen duong a b
Output: 0 neu false, 1 neu true
*/

#include <iostream>

using namespace std;

int tinhTongUocSo(int a);

int ktraSoBanBe(int a, int b);

int main() {
    int a, b;
    cin >> a >> b;

    if (a <= 0 || b <= 0) {
        cout << "Sai input";
        return 0;
    }

    cout << ktraSoBanBe(a, b);

    return 0;
}

int tinhTongUocSo(int a) {
    int result(0);
    for (int i = 1; i < a; i++) {
        if (a % i == 0) result += i;
    }

    return result;
}

int ktraSoBanBe(int a, int b) {
    return 1 * (tinhTongUocSo(a) == b && tinhTongUocSo(b) == a);
}

