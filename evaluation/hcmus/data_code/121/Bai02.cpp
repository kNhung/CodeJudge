#include <iostream>
#include <string.h>
using namespace std;

const int MAX = 100;

int count_occurences(char a[], int n, char x)
{
    int count = 0;

    for (int i = 0; i < n; i++)
    {
        if (a[i] == x)
            count++;
    }

    return count;
}

void del_chars(char a[], int n)
{
    int max = 0;

    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n - 1; j++)
        {
            int occurences = count_occurences(a, n, a[j]);
            if (a[j] == a[i] && occurences > 1)
            {
                a[j] = a[i + 1];
            }
        }
    }
}

void print_name(char a[])
{
    int n = sizeof(a) / sizeof(a[0]);
    for (int i = 0; i < n; i++)
    {
        cout << a[i];
    }
}

int main()
{
    char e[MAX];
    cin.getline(e, MAX);
    int n = sizeof(e) / sizeof(e[0]);

    del_chars(e, n);
    print_name(e);

    return 0;
}