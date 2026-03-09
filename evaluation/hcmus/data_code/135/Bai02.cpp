#include <iostream>
#include <cstring>

using namespace std;

void deleteAt(char a[], int pos)
{
    for (int i = pos; i < strlen(a); i++)
        a[i] = a[i + 1];

    a[strlen(a)] = '\0';
}

void xoaTrung(char a[])
{
    char w[100];


    for (int i = 0; i < strlen(a); i++)
    {
        w[0] = a[i];
        for (int j = 1; i < strlen(a); j++)
            if (a[j] == w[0])
                deleteAt(a, i);
    }

    cout <<a;
}



int main()
{
    char a[100];
    cout <<"Input: ";
    cin >>a;

    xoaTrung(a);
    return 0;
}