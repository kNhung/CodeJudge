// Bai04.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
using namespace std;

void nhap(int& a, int& b)
{
    cin >> a >> b;
    while (a < 1 || b < 1)
    {
        cin >> a >> b;
    }
}

int tongUocSo(int n)
{
    int sum = 1;
    for (int i = 2; i < n; i++)
    {
        if (n % i == 0)
            sum += i;
    }
    return sum;
}

int kiemTraSoBanBe(int a, int b)
{
    if (tongUocSo(a) == b && tongUocSo(b) == a)
    {
        return 1;
    }
    return 0;
}

int main()
{
    int a, b;
    nhap(a, b);
    cout << kiemTraSoBanBe(a, b) << endl;

    return 0;
}

