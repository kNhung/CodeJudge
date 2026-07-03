#include <iostream>
#include <string.h>
using namespace std;

const int MAX = 1000;

struct Team
{
    char name[MAX];
    unsigned likes;
    unsigned comments;
    unsigned shares;

    int marks;
};

void input_team(Team list[])
{
    int i = 0;
    char done[3] = {'0', '0', '0'};
    do
    {
        cout << "Name: ";
        cin.getline(list[i].name, MAX);
        cout << "Like: ";
        cin >> list[i].likes;
        cout << "Comment: ";
        cin >> list[i].comments;
        cout << "Share: ";
        cin >> list[i].shares;

        list[i].marks = list[i].likes * 1 + list[i].comments * 2 + list[i].shares * 3;
        i++;
        cin.ignore();
    } while (!strcmp(list[i].name, done));
}

void print_name(char a[])
{
    int n = sizeof(a) / sizeof(a[0]);
    for (int i = 0; i < n; i++)
    {
        cout << a[i];
    }
}

void print_compare(Team list[])
{
    int n = sizeof(list) / sizeof(list[0]);
    int max_mark = list[0].marks;
    int location;
    int mark_list[n];

    for (int i = 0; i < n; i++)
    {
        if (list[i].marks > max_mark)
        {
            max_mark = list[i].marks;
            location = i;
        }
    }

    for (int i = 0; i < n; i++)
    {
        if (list[i].marks == max_mark)
        {
            print_name(list[i].name);
            cout << "|" << endl;
        }
    }
}

int main()
{
    Team list[MAX];

    input_team(list);
    print_compare(list);

    return 0;
}