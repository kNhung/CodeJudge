#include <iostream>

int getInt()
{
    int temp{};
    std::cin >> temp;
    return temp;
}

bool checkEven(int num)
{
    return num % 2 == 0;
}

int main()
{
    std::cout << "Nhap a: ";
    int a{getInt()};
    std::cout << "Nhap b: ";
    int b{getInt()};

    if (a > b)
        std::cout << "Du lieu nhap sai\n";
    else
    {
        int sum{0};

        for (int count{a}; count <= b; ++count)
        {
            if (checkEven(count))
                sum += count;
        }

        std::cout << sum;
    }
    return 0;
}
