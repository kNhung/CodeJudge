#include <iostream>

using namespace std;

/*
Viet chuong trinh kiem tra 1 cap so nguyen co phai so ban be hay khong
*/

int tinhUocSo(int a, int b)
{
    int sum_a = 0;
    int sum_b = 0;
    for (int i = 1; i < a; i++)
    {
        if (a % i == 0)
            sum_a += i;    //tinh tong cac uoc cua a
    }
    for (int i = 1; i < b; i++)
    {
        if (b % i == 0)
            sum_b += i;  // tinh tong cac uoc cua b
    }
    if (sum_a == b && sum_b == a) return 1;
    return 0;
}

int main()
{
    int a, b;
    cin >>a;
    cin >>b;

    cout <<tinhUocSo(a,b);
}