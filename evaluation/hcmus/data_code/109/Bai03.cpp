#include <iostream>
#include <cstring>

struct Team
{
    char name[40];
    int likes;
    int comments;
    int shares;
};

void inputTeam(Team a)
{
    char tmp_name[40];

    do 
    {
        std::cout << "Ten: ";
        std::cin.getline(tmp_name, 40);

        if (strcmp(tmp_name, "000") != 0)
        {
            strcpy(a.name, tmp_name);

            std::cout << "Luot like: ";
            std::cin >> a.likes;

            std::cout << "Luot comment: ";
            std::cin >> a.comments;

            std::cout << "Luot share: ";
            std::cin >> a.shares;

            std::cin.ignore();
        }
    }
    while (strcmp("000", tmp_name) != 0);

}

int main()
{
    int n = 0;
    Team teams[100];

    inputTeam(teams[n++]);

    return 0;
}