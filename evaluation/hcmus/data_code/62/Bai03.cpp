#include<iostream>
using namespace std;

int daoSo (int n)
{
    int temp = n, nDao = 0;
    while (temp > 0)
    {
        int i = temp%10;
        nDao = nDao*10 + i;
        temp/=10;
    }
    return nDao;
}

void inSoDoiXung (int n)
{
    int max = -1, t = 1;
    while (t <= 10000)
    {
        int temp = n;
        t*=10;
        int x = 0;
        if (temp%t >= 10)
            x = ((temp%t)%(t/10));
        temp = ((temp/t)*(t/10)) + x;
        if (daoSo(temp) == temp && temp >= max)
            max = temp;
    }
    cout << max;
}

int main ()
{
    int n;
    cin >> n;
    if (n >= 1000 && n <= 9999)
        inSoDoiXung(n);
    else
        cout << "Nhap lai";

    return 0;
}