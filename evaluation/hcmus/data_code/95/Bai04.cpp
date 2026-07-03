#include <iostream>

int getInt()
{
    int temp{};
    std::cin >> temp;
    return temp;
}

int sumDiv(int num)
{
    if (num <= 0)
        return 0;

    int sum{0};

    for (int count{1}; count < num; ++count)
    {
        sum += count * (num % count == 0);
    }

    return sum;
}

int main()
{
    std::cout << "Nhap a: ";
    int a{getInt()};
    std::cout << "Nhap b: ";
    int b{getInt()};

    if (a <= 0 || b <= 0)
        std::cout << "Du lieu nhap sai\n";
    else
    {
        if (sumDiv(a) == b && sumDiv(b) == a)
            std::cout << "1\n";
        else
            std::cout << "0\n";
    }
    return 0;
}
