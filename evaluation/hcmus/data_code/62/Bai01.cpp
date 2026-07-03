#include<iostream>
using namespace std;

int tinhTong (int a, int b)
{
    int Sum = 0;
    for (int i = a; i <= b; i++)
    {
        if (i%2 == 0)
            Sum += i;
    }
    return Sum;
}

int main ()
{
    int a, b;
    cin >> a >> b;
    if (a <= b)
        cout << tinhTong (a, b);
    else
        cout << "Nhap lai";

    return 0;
}