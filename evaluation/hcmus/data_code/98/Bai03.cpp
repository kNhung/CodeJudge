#include <iostream>
#include <cstring>
using namespace std;

#define MAX 100
struct Team
{
    char name[40];
    int like;
    int comment;
    int share;
};

void nhap1Team(Team &team)
{
    cout << "Nhap ten doi: ";
    cin.getline(team.name, 40);
    cout << "Nhap so luot like: ";
    cin >> team.like;
    cout << "Nhap so luot comment: ";
    cin >> team.comment;
    cout << "Nhap so luot share: ";
    cin >> team.share;
    cin.ignore();
}

void nhapCacTeam(Team team[MAX])
{
    for (int i = 0; i < MAX; i++)
    {
        nhap1Team(team[i]);
        if (strcmp(team[i].name, "000") == 0)
            break;
    }
}

int ketQua1Team(Team team)
{
    return (team.like + team.comment * 2 + team.share * 3);
}

// void sapXepDiem(Team team[MAX])
// {
//     int max = ketQua1Team(team[0]);
//     for (int i = 0; i < MAX; i++)
//     {
//         if (ketQua1Team(team[i]) > max)
//             max = ketQua1Team(team[i]);
//     }
//     for (int i = 0; i < MAX; i++)
//     {
//         if (ketQua1Team(team[i]) == max)
//             cout << team[i].name << endl;
//     }
// }
int main()
{
    Team team[MAX];
    nhapCacTeam(team);
    //sapXepDiem(team);
    return 0;
}