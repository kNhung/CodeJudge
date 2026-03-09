#include <iostream>
#include <cmath>
#include <cstring>

void removeDupeChar(char str[])
{
    for (int i{0}; i < strlen(str); ++i)
    {
        if (str[i] == str[i + 1])
        {
            for (int k{i + 1}; k < strlen(str); ++k)
            {
                str[k] = str[k + 1];
            }
            for (int k{i}; k < strlen(str); ++k)
            {
                str[k] = str[k + 1];
            }
            i = -1;
        }
    }
}

int main()
{
    return 0;
}
