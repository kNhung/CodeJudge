#include <iostream>
#include <cstring>

using namespace std;

void xoa(char s[], int post, int b[]){
    for (int i = b[post] + 1; i >= 1; i--)
    {       
        for (int j = post; j < strlen(s); j++)
        {
            s[j] = s[j + 1];
        }
        s[strlen(s)] = '\0';
        post--;
    }
    for (int i = post; i >= post - b[post]; i--)
    {
        b[i] = 0;
    }
}

void xoachugiongnhau(char s[], int a[], int b[])
{
    int tmp = 1;
    int max = 0;
    cin.getline(s, 256);
    while (tmp != 0)
    {
    for (int i = 0; i < strlen(s); i++)
    {
        a[i] = static_cast<int>(s[i]);
    }
    for (int i = 1; i < strlen(s); i++)
    {
        if (a[i] == a[i - 1])
        {
            b[i] = b[i-1] + 1;
        }
    }
    int tmp = 0;
    for (int i = 0; i < strlen(s); i++)
    {
        if (b[max] < b[i])
        max = i;
        tmp = b[max];
    }
    xoa(s, max, b);
    cout << s;
    a[256] = {0};
    b[256] = {0};
    }
}

int main(){
    return 0;
}