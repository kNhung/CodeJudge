#include <iostream>
#include <cstring>
#include <cmath>

using namespace std;

#define MAX 1000

void deleteDuplicate(char s[])
{
    int n = strlen(s);
    //cout << n << endl;
    for (int i = 0; i < n; i++)
    {
        if (s[i] == s[i + 1])
        {
            for (int j = i; j < n; j++)
            {
                s[j] = s[j + 1];
            }
            //cout << s << endl;
            n--;
            i--;
        }
    }
}

int main()
{
    char s[MAX];

    cin.getline(s, MAX);
    deleteDuplicate(s);

    cout << s;

    return 0;
}