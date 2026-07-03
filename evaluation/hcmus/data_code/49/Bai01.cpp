#include <iostream>

using namespace std;

int sumOdd(int a, int b)
{
    int sum = 0;
    for (int i = a; i <= b; i++)
        if (i % 2 == 0)
            sum = sum + i;
    return sum;
}

int main()
{
    int a, b;
    int sum = 0;

    do
    {
        cin >> a >> b;
    } while (a < 0 || b < 0);

    sum = sumOdd(a, b);
    cout << "Sum = " << sum << endl;

    return 0;
}