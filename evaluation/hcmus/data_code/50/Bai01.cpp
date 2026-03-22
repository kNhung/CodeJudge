// Cau1.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
using namespace std;

void nhap(int& a, int& b)
{
    cin >> a;
    cin >> b;
}

int tinhTongSoChan(int a, int b)
{
    int sum = 0;
    for (int i = a; i <= b; i++)
    {
        if (i % 2 == 0)
        {
            sum += i;
        }
    }
    return sum;
}

int main()
{
    int a, b;
    nhap(a, b);
    cout << "Tong cac so chan trong khoang tu a den b la: " << tinhTongSoChan(a, b) << endl;
    return 0;
}


