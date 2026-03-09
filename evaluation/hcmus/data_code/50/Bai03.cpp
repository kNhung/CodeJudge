// Bai03.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
using namespace std;

void nhap(int& a)
{
    cin >> a;
    while (a < 1000 || a > 9999 )
    {
        cin >> a;
    }
}

int soDoiXung(int n)
{
    int reversedNum = 0;
    while (n != 0)
    {
        int temp = n % 10;
        reversedNum = temp + reversedNum * 10;
        n /= 10;
    }
    return reversedNum;
}

bool kiemTraSoDoiXung(int n)
{
    if (soDoiXung(n) == n)
        return true;
    else
        return false;
}

int soDoiXungLonNhatSauKhiXoa1ChuSo(int n)
{
    /*neu da la so doi xung thi khong xoa*/
    if (kiemTraSoDoiXung(n))
        return n;

    else
    {

    }
}


int main()
{
    int n;
    nhap(n);

    cout << soDoiXungLonNhatSauKhiXoa1ChuSo(n) << endl;
    return 0;
}

