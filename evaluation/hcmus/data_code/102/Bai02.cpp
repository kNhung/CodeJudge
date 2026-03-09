#include <iostream>
#include <cstring>

using namespace std;
#define MAX 1000

void deleteAtPos(char ch[], int pos)
{
    for (int i = pos; i < strlen(ch) - 2; i++)
    {
        ch[i] = ch[i + 2];
    }
    ch[strlen(ch) - 2] = '\0';
}
int main()
{
    char ch[MAX];
    cin >> ch;

    for (int j = 0; j < strlen(ch); j++)
    {
        for (int i = 0; i < strlen(ch); i++)
        {
            if (ch[i] == ch[i + 1])
            {
                deleteAtPos(ch, i);
                i--;
            }
        }
    }

    cout << ch;

    return 0;
}