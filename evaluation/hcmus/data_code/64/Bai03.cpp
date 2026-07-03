/*
Ho ten: Le Nguyen Nhat Truong
Lop: 23CLC02
MSSV: 23127136

Bai 3 - De thi giua ki (thuc hanh)
Chuong trinh: in ra so doi xung lon nhat tao thanh tu viec xoa 1 so bat ki trong n

Input: so nguyen duong n (1000 <= n <= 9999)
Output: so lon nhat tao thanh
*/

#include <iostream>
#include <cmath>

using namespace std;

int xoaChuSo(int n, int chu);

int demSoChuSo(int a);

bool ktraDoiXung(int a);

int main() {
    int n;
    cin >> n;

    if (1000 > n || n > 9999) {
        cout << "Sai input";
        return 0;
    }

    if (ktraDoiXung(n)) {
        cout << n;
        return 0;
    }

    int ketQua = -1;

    for (int i = 1; i <= 4; i++) {
        int soMoi = xoaChuSo(n, i);
        if (ktraDoiXung(soMoi) && soMoi >= ketQua) {
            ketQua = soMoi;
        }
    }

    cout << ketQua;

    return 0;
}

int xoaChuSo(int n, int chu) {
    int pow10 = 1;
    for (int i = 1; i <= chu; i++) {
        pow10 *= 10;
    }
    return int((n / pow10) * (pow10 / 10)) + (n % (pow10 / 10));
}

int demSoChuSo(int a) {
    int temp = a, countChuSo(0);
    while (temp > 0) {
        int chuSo = temp % 10;
        int luuSoLap;
        for (int i = 0; i <= 9; i++) {
            if (i == chuSo && luuSoLap != i) {
                luuSoLap = i;
                countChuSo++;
                break;
            }
        }
        temp /= 10;
    }

    return countChuSo;
}

bool ktraDoiXung(int a) {
    if (demSoChuSo(a) < 2) return false;

    int soDocTuPhai = (a % 10);

    for (int i = a / 10; i > 0; i /= 10) {
        soDocTuPhai *= 10;
        soDocTuPhai += (i % 10);
    }

    return (soDocTuPhai == a);
}