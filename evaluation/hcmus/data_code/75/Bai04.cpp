#include <iostream>
using namespace std;

int TinhTongCacUocSo (int n)
{
    int sum = 0;
    for (int i = 1; i < n; i++)
    {
        if (n % i == 0)
        {
            sum = sum + i;
        }
    }
    return sum;
}

bool KtraSoBanBe (int a, int b)
{
    int SumA = TinhTongCacUocSo (a);
    int SumB = TinhTongCacUocSo (b);
    
    if (SumA == b && SumB == a) return 1;
    else return 0;
}

int main ()
{
    float a, b;
    cin >> a;
    cin >> b;
    if (int (a) == a && int (b) == b && a > 0 && b > 0)
    {
        cout << KtraSoBanBe (a, b);
        return 0;
    }
    else 
    {
        cout << "Error";
        return 0;
    }
}