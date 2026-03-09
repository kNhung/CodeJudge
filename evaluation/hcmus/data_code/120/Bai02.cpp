/*
23CLC02 - 23127266 - NGUYEN ANH THU
BAI 2
Input:
Output:
*/
#include <iostream>
#include <cstring>
using namespace std;

int check(char str[])
{
    for (int i = 1; i < strlen(str); i++)
        if (str[i] == str[i - 1])
            return 1;
    return 0;
}

void xoa(char str[])
{
    while (check(str))
    {
        int dem = 0;
        char xau[100] = "";

        int n = strlen(str);

        if (str[0] != str[1])
            xau[dem++] = str[0];

        for (int i = 1; i < n - 1; i++)
            if (str[i] != str[i + 1] && str[i] != str[i - 1])
            {
                xau[dem++] = str[i];
            }

        if (n > 1)
            if (str[n - 1] != str[n - 2])
                xau[dem++] = str[n - 1];

        strcpy(str, xau);
    }
    cout << str;
}
int main()
{
    char str[101];

    cin >> str;

    xoa(str);

    return 0;
}