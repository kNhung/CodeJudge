#include <iostream>
#define MAX 1000

using namespace std;

void xoaChuCaiTrungNhau(char s[])
{
    int len = strlen(s);
    int j = 0; 

    for (int i = 0; i < len; i++) 
    {
        if (j > 0 && s[j - 1] == s[i]) 
        {
            
            while (j > 0 && s[j - 1] == s[i]) 
            {
                j--; 
            }
        }
        else 
        {
            s[j] = s[i]; 
            j++;
        }
    }
    s[j] = '\0';
}

int main() 
{
    char s[] = "abbaca";
    xoaChuCaiTrungNhau(s);
    cout << "Output: " << s;
    return 0;
}
