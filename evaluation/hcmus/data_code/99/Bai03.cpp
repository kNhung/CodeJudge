#pragma warning(disable:4996)
#include <iostream>
#include <cstring>
#define MAXName 40
#define MAXTeams 100
using namespace std;

struct Team
{
    char name[MAXName];
    int like, comment, share;
};

bool strCompare(char str1[], char str2[]) 
{
    int i = 0;
    while (str1[i] != '\0' && str2[i] != '\0') 
    {
        if (str1[i] != str2[i]) 
        {
            return false;
        }
        i++;
    }
    return str1[i] == str2[i];
}

void copyCharArr(char source[], char destination[])
{
	int i = 0;
    while (source[i] != '\0')
    {
		destination[i] = source[i];
		i++;
	}
	destination[i] = '\0';
}

int calculateScore(const Team& team)
{
    return team.like + 2 * team.comment + 3 * team.share;
}

char name0[] = "000";

void inputTeam(Team& team)
{
    cout << "Name: ";
    cin.ignore();
    cin.getline(team.name, MAXName);
    if (strCompare(team.name, name0)) return;

    cout << "Like: ";
    cin >> team.like;
    cout << "Comment: ";
    cin >> team.comment;
    cout << "Share: ";
    cin >> team.share;
}

void inputTeams(Team teams[], int& n)
{
    n = 0;
    while (true)
    {
        inputTeam(teams[n]);
        if (strcmp(teams[n].name, "000") == 0)
        {
            break;
        }
        n++;
    }
}

void printTeams(const Team teams[], int n)
{
    for (int i = 0; i < n; i++)
    {
        cout << teams[i].name << endl;
    }
}

void copyTeams(const Team source[], Team destination[], int n)
{
    for (int i = 0; i < n; i++)
    {
        strcpy(destination[i].name, source[i].name);
        destination[i].like = source[i].like;
        destination[i].comment = source[i].comment;
        destination[i].share = source[i].share;
    }
}


void findTop3(Team teams[], int n)
{
    for (int i = 0; i < n - 1; i++)
    {
        int max = i;
        for (int j = i + 1; j < n; j++)
        {
            if (calculateScore(teams[j]) > calculateScore(teams[max]) ||
                (calculateScore(teams[j]) == calculateScore(teams[max]) &&
                    (teams[j].share > teams[max].share ||
                        (teams[j].share == teams[max].share &&
                            (teams[j].comment > teams[max].comment ||
                                (teams[j].comment == teams[max].comment && teams[j].like > teams[max].like))))))
            {
                max = j;
            }
        }
        swap(teams[i], teams[max]);
    }
}

int min(int a, int b)
{
	return a < b ? a : b;
}

int main()
{
    Team teams[MAXTeams];
    Team teams2[MAXTeams];
    int numbers = 0;
    inputTeams(teams, numbers);
    cout << "Input teams: " << endl;
    printTeams(teams, numbers);
    copyTeams(teams, teams2, numbers);
    findTop3(teams2, numbers);
    cout << "\nTop 3: " << endl;
    printTeams(teams2, min(numbers, 3));
    return 0;
}
