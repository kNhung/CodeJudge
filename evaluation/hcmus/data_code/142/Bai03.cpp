#include <iostream>
#include <cmath>
#include <cstring>

struct Team
{
    char name[40]{};
    int like{};
    int comment{};
    int share{};
};

int inputTeam(Team team[])
{
    int i{0};
    while (strcmp(team[i - 1].name, "000\0") != 0)
    {
        std::cout << "- Name: ";
        std::cin.getline(team[i].name, 40);
        if (strcmp(team[i].name, "000\0") != 0)
        {
            std::cout << "- Like: ";
            std::cin >> team[i].like;

            std::cout << "- Comment: ";
            std::cin >> team[i].comment;

            std::cout << "- Share: ";
            std::cin >> team[i].share;

            std::cin.ignore();
        }

        ++i;
    }

    return i;
}

void calcScore(Team team[], int arr[], int n)
{
    for (int i{0}; i < n; ++i)
    {
        arr[i] = team[i].like + team[i].comment * 2 + team[i].share * 3;
    }
}

void sortArr(Team team[], int arr[], int n)
{
    int max{arr[0]};
    int maxIdx{0};
    Team maxTeam{team[0]};

    int swap{0};
    for (int j{0}; j < n; ++j)
    {
        for (int i{j}; i < n; ++i)
        {
            if (max < arr[i])
            {
                max = arr[i];
                maxIdx = i;
                maxTeam = team[i];
            }
        }
        arr[maxIdx] = arr[j];
        arr[j] = max;
        max = arr[j + 1];

        team[maxIdx] = team[j];
        team[j] = maxTeam;
        maxTeam = team[j + 1];
    }
}

int main()
{
    Team team[100]{};
    int arr[100]{};
    int count{0};

    count = inputTeam(team);
    calcScore(team, arr, count);
    sortArr(team, arr, count);

    bool checkSame{0};
    Team temp{};
    for (int i{0}; i < 3; ++i)
    {
        for (int j{i + 1}; j < count; ++j)
        {
            if (arr[i] != arr[j] && team[j].share > team[i].share)
                temp = team[j];
            else if (arr[i] != arr[j] && team[j].comment > team[i].comment && team[j].share == team[i].share)
                temp = team[j];
            else if (arr[i] != arr[j] && team[j].like > team[i].like && team[j].comment == team[i].comment && team[j].share == team[i].share)
                temp = team[j];
            else
                temp = team[i];
        }
        std::cout << temp.name << '\n';
    }
    return 0;
}
