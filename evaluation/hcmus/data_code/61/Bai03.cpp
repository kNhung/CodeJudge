#include <iostream>

int checkDoiXung(int n);

int main()
{
    int n;
    std::cin >> n;

    if (checkDoiXung(n) == 1)
        std::cout << n << "\n";
    else
    {
        int len = 0;
        for (int i = n; i > 0; i /= 10)
            len++;

        int max_digit = 0;
        for (int i = n; i > 0; i /= 10)
        {
            if (i % 10 > max_digit)
                max_digit = i % 10;
        }


        int max_freq = 0;
        int max_freq_digit = 0;
        for (int i = n; i > 0; i /= 10)
        {
            int freq = 1;
            for (int j = i / 10; j > 0; j /= 10)
            {
                if (j % 10 == i % 10)
                    freq++;
            }
            if (max_freq < freq)
            {
                max_freq = freq;
                max_freq_digit = i % 10;
            }
        }


        std::cout << max_freq_digit;
        std::cout << max_digit;
        std::cout << max_freq_digit;
    }

    return 0;
}

int checkDoiXung(int n)
{
    int len = 0;
    for (int i = n; i > 0; i /= 10)
        len++;

    int reverse_n = 0;
    for (int i = n; i > 0; i /= 10)
    {
        int digit = i % 10;
        for (int j = 1; j < len; j++)
            digit *= 10;
        reverse_n += digit;
        len--;
    }

    if (reverse_n == n)
        return 1;
    else
        return 0;
}
