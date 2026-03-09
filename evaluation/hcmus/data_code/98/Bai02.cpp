#include <iostream>
#include <cstring>
using namespace std;

#define MAX 100

void xoaChuCaiTrungNamLienTiepNhau(char s[])
{
    int n = strlen(s);
    for (int i = 0; i < n; i++)
    {
        if (s[i] == s[i + 1])
        {
            for (int j = i; j < n; j++)
            {
                s[j] = s[j + 2];
            }
            n--;
            i--;
        }
        if(s[i] == s[i + 1])
        {
            i--;
        }
    }
}


int main()
{
    char s[MAX];
    cout << "Nhap chuoi: ";
    cin.getline(s, MAX);
    xoaChuCaiTrungNamLienTiepNhau(s);
    cout << s << endl;
    return 0;
}