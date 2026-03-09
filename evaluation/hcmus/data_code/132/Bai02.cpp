#include <iostream>
#include <cstring>
using namespace std;

int dup(char s[],int &len)
{
    for(int i = 0;i < len;i++)
    {
        if(s[i] == s[i + 1]) return i + 2;
    }
    return -1;
}

int main()
{
    char s[256];
    cin.getline(s,256);
    int len = strlen(s);
    while(dup(s,len) > -1)
    {
        for(int i = dup(s,len);i < len;i++)
            s[i - 2] = s[i];
        len -= 2;
    }

    for(int i = 0;i < len;i++)
        cout << s[i];
    return 0;
}
