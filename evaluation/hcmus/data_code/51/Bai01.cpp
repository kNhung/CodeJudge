#include <iostream>
using namespace std;

void swap(int& a, int& b)
{
    int temp = a;
    a = b;
    b = temp;
}

int sumIntAtoB(int a, int b)
{
    if (a > b)
    {
        swap(a, b);
    }
    int sum = 0;
    for (int i = a; i <= b; i++)
    {
        if (i % 2 == 0)
        {
            sum += i;
        }
    }
    return sum;
}

int main()
{
    int a, b;
    cout << "Please enter int a: ";
    cin >> a;
    cout << "Please enter int b: ";
    cin >> b;
    cout << "Sum even numbers from " << a << " to " << b << " is: " << sumIntAtoB(a, b) << endl;
    return 0;
}
