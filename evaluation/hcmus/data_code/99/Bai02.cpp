#include <iostream>
#include <cstring>
using namespace std;

void deleteDuplicate(char s[], int& n)
{
    n = strlen(s);
    int j = 0;

    for (int i = 1; i < n; i++)
    {
        if (s[j] != s[i])
        {
            s[++j] = s[i];
        }
        else
        {
            while (i < n && s[j] == s[i])
            {
                i++;
            }
            i--; 
            j--;
        }
    }
    s[++j] = '\0';
}

int main()
{
    char s[] = { "abbaca" };
    int n;
    deleteDuplicate(s, n);
    cout << s;
    return 0;
}
