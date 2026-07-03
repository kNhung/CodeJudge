#include <iostream>

int getInt()
{
    int temp{};
    std::cin >> temp;
    return temp;
}

bool checkEquReversed(int num, int base10)
{
    int reversedNum{0};
    int temp{num};

    while (temp != 0)
    {
        reversedNum = reversedNum + (temp % 10) * base10;
        base10 /= 10;
        temp /= 10;
    }

    return num == reversedNum;
}

int main()
{
    std::cout << "Nhap n: ";
    int n{getInt()};

    if (n <= 1000 || n >= 9999)
        std::cout << "Du lieu nhap sai\n";
    else
    {
        int base10{1};
        int largestRe{n * checkEquReversed(n, 1000)};

        while (base10 != 10000)
        {
            int temp{n};
            int digit{temp % (base10)};
            temp = (temp / (base10 * 10)) * base10 + digit;
            base10 *= 10;

            if (checkEquReversed(temp, 100) && temp > largestRe)
                largestRe = temp;
        }

        base10 = 1;

        while (base10 != 1000)
        {
            int temp{n};
            int digit{temp % (base10)};
            temp = (temp / (base10 * 100)) * base10 + digit;
            base10 *= 10;

            std::cout << temp << '\n';
            if (checkEquReversed(temp, 10) && temp > largestRe)
                largestRe = temp;
        }

        if (checkEquReversed(n % 1000 / 10, 10) && (n % 1000 / 10) > largestRe)
            largestRe = n % 1000 / 10;

        std::cout << largestRe << '\n';
    }
    return 0;
}
