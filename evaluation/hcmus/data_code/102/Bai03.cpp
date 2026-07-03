#include <iostream>
#include <cstring>

using namespace std;

struct Team
{
    char name[40];
    int like;
    int cmt;
    int share;
    int point;

    void print()
    {
        cout << endl;
        cout << name << endl;
        cout << cmt << endl;
        cout << share << endl;
        cout << point << endl;
    }
};
int main()
{
    Team teams[1000];
    char temp[1000] = "";

    int count = 0;

    while (true)
    {
        cin >> temp;
        cin >> teams[count].name;
        if (strcmp(teams[count].name, "000") == 0)
            break;

        cin >> temp;
        cin >> teams[count].like;
        strcpy(temp, "");

        cin >> temp;
        cin >> teams[count].cmt;
        strcpy(temp, "");

        cin >> temp;
        cin >> teams[count].share;
        strcpy(temp, "");

        count++;
    }

    for (int i = 0; i < count; i++)
    {
        teams[i].point = teams[i].like + teams[i].cmt * 2 + teams[i].share * 3;
    }

    for (int i = 0; i < count - 1; i++)
    {
        for (int j = i + 1; j < count; j++)
        {
            if (teams[i].point > teams[j].point)
            {
                swap(teams[i].name, teams[j].name);
                swap(teams[i].cmt, teams[j].cmt);
                swap(teams[i].like, teams[j].like);
                swap(teams[i].share, teams[j].share);
                swap(teams[i].point, teams[j].point);
            }
        }
    }

    for (int i = 0; i < 3; i++)
    {
        if (strcmp(teams[i].name, "000") != 0)
        cout << teams[i].name << endl;
    }

    return 0;
}