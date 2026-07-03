#include <iostream>
using namespace std;

int automorphic(int n)
{
    int automorph = n * n;
    int second_n(0);

    for (int i = 1; automorph != 0; i = i * 10)
    {
        int remainder = automorph % 10;
        second_n = second_n + remainder * i;

        if (second_n == n)
            return 1;

        automorph = automorph / 10;
    }

    return 0;
}

int main()
{
    int n;
    cin >> n;

    if (n <= 0)
    {
        cout << "Error!";
    }
    else
    {
        cout << automorphic(n);
    }

    return 0;
}