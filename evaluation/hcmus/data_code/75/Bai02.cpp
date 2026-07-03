#include <iostream>
using namespace std;

int pow (int a, int b)
{
    int ketqua = 1;
    for (int i = 1; i <= b; i++)
    {
        ketqua = ketqua * a;
    }
    return ketqua;
}

int CountNumber (int n)
{
    int count = 0;
    
    while (n != 0)
    {
        n = n / 10;
        count ++;
    }

    return count;
}

bool CheckAutomorphic (int n)
{
    int a = CountNumber (n);
    int m = n * n;
    int h = m;
    m = m / pow (10, a);
    m = h - m * pow (10, a);
    if (m == n) return 1;
    else return 0;
}

int main ()
{
    float n;
    cin >> n;

    if (int (n) == n && n > 0)
    {
        cout << CheckAutomorphic (n);
        return 0;
    }
    else 
    {
        cout << "Error";
        return 0;
    }
}