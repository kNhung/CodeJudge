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
    std::cout << "Nhap n: ";
    int n{getInt()};

    if (n <= 0)
        std::cout << "Du lieu nhap sai\n";
    else
    {
        int square{n * n};

        int temp{0};
        int base10{1};
        int digit{0};
        bool checkExe{0};

        while (square != 0)
        {
            digit = square % 10;
            temp = digit * base10 + temp;
            base10 *= 10;
            square /= 10;
            if (temp == n)
            {
                checkExe = 1;
                std::cout << "1\n";
                break;
            }
        }

        if (!checkExe)
            std::cout << "0\n";
    }
    return 0;
}
