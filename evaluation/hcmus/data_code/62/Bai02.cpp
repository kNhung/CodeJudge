#include<iostream>
#include<cmath>
using namespace std;

bool checkSo (int n)
{
    int t = 1, nBinh = pow(n,2), Sum = 0;
    while (nBinh > 0)
    {
        int i = nBinh%10;
        Sum = Sum + i*t;
        if (Sum == n)
            return true;
        t*=10;
        nBinh/=10;
    }
    return false;
}

int main ()
{
    int n;
    cin >> n;
    if (n > 0)
        if ((checkSo(n)))
            cout << "1";
        else
            cout << "0";
    else
        cout << "Nhap lai";

    return 0;
}