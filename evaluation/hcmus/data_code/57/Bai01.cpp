#include<iostream>
using namespace std;

int calculateSum(int a, int b);
void check(int &a, int &b);

int main()
{
    int a;
    cout << "Nhap a: ";
    cin >> a;

    int b;
    cout << "Nhap b: ";
    cin >> b;
    
    check(a,b);

    cout << calculateSum(a,b);

    return 0;
}

int calculateSum(int a, int b)
{
    int Sum = 0;

    for(int i = a; i <= b; i++)
    {
        if(i % 2 == 0)
            Sum = Sum + i;
    }

    return Sum;
}

void check(int &a, int &b)
{
    while(a > b)
    {
        cout << "Khong hop le!" << endl;
        cout << "Moi nhap lai" << endl;

        cout << "Nhap a: ";
        cin >> a;

        cout << "Nhap b: ";
        cin >> b;
    }
}