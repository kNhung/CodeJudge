#include <iostream>
using namespace std;

int TinhTongCacSoChan (int a, int b)
{
    int sum = 0;
    
    for (int i = a; i <= b; i++)
    {
        if (i % 2 == 0)
        {
            sum = sum + i;
        }
    }
    
    return sum;
}

int main ()
{
    float a,b;
    cin >> a;
    cin >> b;
    int sum = TinhTongCacSoChan (a, b);
    
    if (a <= b && int (a) == a && int (b) == b)
    {
        cout << sum;
        return 0;
    }
    else 
    {
        cout << "Error";
        return 0;
    }
}