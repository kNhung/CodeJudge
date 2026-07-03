#include <iostream>

int tinhTonguoc(int n);

int main()
{
    int a, b;
    std::cin >> a >> b;

    if (tinhTonguoc(a) == b && tinhTonguoc(b) == a)
        std::cout << 1 << "\n";
    else
        std::cout << 0 << "\n";
    return 0;
}

int tinhTonguoc(int n)
{
    int sum = 0;
    for (int i = 1; i < n; i++)
    {
        if (n % i == 0)
            sum += i;
    }
    return sum;
}
