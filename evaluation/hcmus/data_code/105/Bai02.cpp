#include<iostream>
#include<cstring>

using namespace std;

#define MAX 100

void xoaChuso(char chr[MAX], int& n)
{
    for(int i = n; i < strlen(chr);i++)
    {
        chr[i] = chr[i + 2];
    }
}

int main()
{
    int n;

    char chr[MAX];

    cin.getline(chr,MAX);


    for(int i = 0; i < strlen(chr)-1; i++)
    {
        if(chr[i]==chr[i+1])
        {
            xoaChuso(chr,i);
            i = i - 1 ;
        }
    }

    cout << chr;

    return 0;
}