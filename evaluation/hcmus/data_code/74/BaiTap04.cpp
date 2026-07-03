#include <iostream>
using namespace std;

int divisor_sum(int x)
{
    int sum(0);

    for (int i = 1; i < x; i++)
    {
        if (x % i == 0)
        {
            sum = sum + i;
        }
    }

    return sum;
}

int friendship_num(int a, int b)
{
    if (divisor_sum(a) == b && divisor_sum(b) == a)
        return 1;

    return 0;
}

int main()
{
    int a, b;
    cin >> a >> b;

    if (a <= 0 || b <= 0)
    {
        cout << "Error!";
    }
    else
    {
        cout << friendship_num(a, b);
    }

    return 0;
}