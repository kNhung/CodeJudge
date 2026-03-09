// De bai:
//  Câu 1. (3đ) Viết chương trình tính tổng các số chẵn trong khoảng từ a đến b,
//  trong đó a và b là hai số nguyên được nhập từ bàn phím (a <= b).
//  VD:
//  Input:
//  Nhập a: 3
//  Nhập b: 10
//  Output: 28

#include <iostream>
#include <cmath>

using namespace std;

int sum(int a, int b)
{
    int s = 0;
    for (int i = a; i <= b; i++)
    {
        if (i % 2 == 0)
            s += i;
    }
    return s;
}

int main()
{
    int a, b;
    cin >> a >> b;
    cout << sum(a, b);

    return 0;
}