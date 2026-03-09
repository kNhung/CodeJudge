#include <iostream>

int main()
{
    int n;
    std::cin >> n;

    if (n > 0)
    {
        int len = 0;
        for (int i = n; i > 0; i /= 10)
            len++;

        int cnt = 1;
        for (int i = 1; i <= len; i++)
            cnt *= 10;

        if (n == (n * n) % cnt)
            std::cout << 1 << "\n";
        else
            std::cout << 0 << "\n";
    }
    else
        std::cout << "Nhap lai n\n";
    return 0;
}
