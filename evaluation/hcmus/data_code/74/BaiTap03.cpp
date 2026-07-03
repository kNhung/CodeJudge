#include <iostream>
using namespace std;

bool mirror_num(int n)
{
    int orginal_n = n;
    int reversed_n(0);

    while (n != 0)
    {
        int remainder = n % 10;
        reversed_n = reversed_n * 10 + remainder;

        if (reversed_n == orginal_n)
            return true;

        n = n / 10;
    }

    return false;
}

int biggest_mirror(int n)
{
    int compare(0);
    if (n >= compare)
        compare = n;

    return compare;
}

int delete_digits(int n)
{
    int new_n;

    if (mirror_num(n))
        return n;

    for (int i = 1; i <= 100000; i = i * 10)
    {
        int remainder = n % i;
        int quotient = n / i;
        new_n = quotient / 10 * i + remainder;

        if (mirror_num(new_n))
        {
            return biggest_mirror(new_n);
        }
    }

    return -1;
}

int main()
{
    int n;
    cin >> n;

    if (n < 1000 || n > 9999)
    {
        cout << "Error!";
    }
    else
    {
        cout << "\n"
             << delete_digits(n);
    }

    return 0;
}