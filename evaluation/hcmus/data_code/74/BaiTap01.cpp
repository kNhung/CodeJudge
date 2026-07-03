#include <iostream>
using namespace std;

int calculate_even(int a, int b)
{
    int sum(0);
    int i = a;

    while (i <= b)
    {
        if (i % 2 == 0)
        {
            sum = sum + i;
        }

        i++;
    }

    return sum;
}

int main()
{
    int a, b;

    cout << "Nhap a: ";
    cin >> a;
    cout << "Nhap b: ";
    cin >> b;

    if (a > b)
    {
        cout << "Error!";
    }
    else
    {
        int sum = calculate_even(a, b);
        cout << sum;
    }
}