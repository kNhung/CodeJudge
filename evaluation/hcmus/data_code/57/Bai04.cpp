#include<iostream>
#include<cmath>

using namespace std;

int tinhTongUoc(int x);
void check(int &a, int &b);

int main()
{
    int a;
    cout << "Nhap a: ";
    cin >> a;

    int b;
    cout << "Nhap b: ";
    cin >> b;

    if((tinhTongUoc(a)==b) && (tinhTongUoc(b)==a))
        cout << 1;
    else
        cout << 0;

    return 0;
}

int tinhTongUoc(int x)
{
    int Sum = 0;
    for(int i = 1; i <= (x-1); i++)
    {
        if(x % i == 0)
            Sum = Sum + i;
    }

    return Sum;
}

void check(int &a, int &b)
{
    while(a <= 0 || b <= 0)
    {
        cout << "Khong hop le! Moi nhap lai!" << endl;
        
        cout << "Nhap a: ";
        cin >> a;

        cout << "Nhap b: ";
        cin >> b;
    }
}