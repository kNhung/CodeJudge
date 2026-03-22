/*
23CLC02 - 23127266 - NGUYEN ANH THU

Input:
Output:
*/
#include <iostream>
#include <cstring>

using namespace std;

struct SV
{
    char Name[50];
    char like[50];
    char comment[50];
    char share[50];
};

int main()
{
    SV sv[100];

    char str[100] = "";
    int soPhanTu = 0;

    while (true)
    {
        cin.getline(str, 100);
        int dem = 0;
        bool ok = 0;
        char data[100] = "";
        for (int i = 0; i < strlen(str); i++)
        {
            if (ok)
                data[dem++] = str[i];
            if (str[i] == ' ')
                if (str[i - 1] == ':')
                    ok = 1;
        }

        strcpy(str, data);

        if (data[0] == 'N')
            strcpy(sv[soPhanTu].Name, data);
        if (data[0] == 'L')
            strcpy(sv[soPhanTu].like, data);
        if (data[0] == 'C')
            strcpy(sv[soPhanTu].comment, data);
        if (data[0] == 'S')
            strcpy(sv[soPhanTu].share, data);

        if (data[0] == '0')
            break;
    }
    return 0;
}