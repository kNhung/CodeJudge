#include <iostream>

int main()
{
    int a, b;
    std::cin >> a >> b;

    if (a <= b)
    {
        int sum = 0;
        for (int i = a; i <= b; i++)
        {
            if (i % 2 == 0)
                sum += i;
        }

        std::cout << sum << "\n";
    }
    else
        std::cout << "Nhap lai a, b\n";

    return 0;
}
