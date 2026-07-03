#include<iostream>
using namespace std;

int tinhTongUoc (int n)
{
    int Sum = 0;
    for (int i = 1; i < n; i++)
    {
        if (n%i == 0)
            Sum += i;
    }
    return Sum;
}

bool checkSoBanBe (int a, int b)
{
    if (tinhTongUoc(a) == b && tinhTongUoc(b) == a)
        return true;
    else
        return false;
}

int main ()
{
    unsigned int a, b;
    cin >> a >> b;
    if (a < 0 || b < 0)
        cout << "Nhap lai";
    else if (checkSoBanBe(a, b))
        cout << "1";
    else
        cout << "0";

    return 0;
}