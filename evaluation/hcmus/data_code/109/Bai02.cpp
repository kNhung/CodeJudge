#include <iostream>
#include <cstring>

void changeCharsArr(char s[])
{
    int n = strlen(s);

    int flag = 0;
    while (flag == 0)
    {
        flag = 1;
        for (int i = 0; i < n - 1; i++)
        {
            if (s[i] == s[i + 1])
            {
                char temp = s[i];
                for (int j = i; j < n; j++)
                {
                    if (s[j] == temp)
                    {
                        s[j] = s[n - 1];
                        s[n - 1] = '\0';
                        n--;
                    }
                }
                flag = 0;
            }
        }
    }

}

int main()
{

    char s[] = "abbaca";

    changeCharsArr(s);
    std::cout << s;
    return 0;
}