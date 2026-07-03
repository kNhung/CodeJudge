#include <iostream>
#include <cmath>
#include <cstring>
using namespace std;

const int MAX_TEAMS = 100;
const int MAX_NAME_LENGTH = 40;

struct Team {
    char name[MAX_NAME_LENGTH];
    int like;
    int comment;
    int share;

    int calculateScore() const {
        return like + 2 * comment + 3 * share;
    }
};

void swapTeams(Team& team1, Team& team2) {
    Team temp = team1;
    team1 = team2;
    team2 = temp;
}

void sortTeams(Team teams[], int size) {
    for (int i = 0; i < size - 1; ++i) {
        for (int j = 0; j < size - i - 1; ++j) {
            if (teams[j].calculateScore() < teams[j + 1].calculateScore()) {
                swapTeams(teams[j], teams[j + 1]);
            }
            else if (teams[j].share < teams[j + 1].share) {
                swapTeams(teams[j], teams[j + 1]);
            }
            else if (teams[j].comment < teams[j + 1].comment) {
                swapTeams(teams[j], teams[j + 1]);
            }
            else if (teams[j].like < teams[j + 1].like) {
                swapTeams(teams[j], teams[j + 1]);
            }
        }
    }
}

int main() {
    Team teams[MAX_TEAMS];
    int teamCount = 0;

    while (true) {
        cout << "Name: ";
        cin.getline(teams[teamCount].name, MAX_NAME_LENGTH);
        if (strcmp(teams[teamCount].name, "000") == 0) {
            break;
        }
        cout << "Like: ";
        cin >> teams[teamCount].like;
        cout << "Comment: ";
        cin >> teams[teamCount].comment;
        cout << "Share: ";
        cin >> teams[teamCount].share;
        cout << endl;
        cin.ignore();

        teamCount++;
    }

    sortTeams(teams, teamCount);

    for (int i = 0; i < std::min(3, teamCount); ++i) {
        cout << teams[i].name << std::endl;
    }

    return 0;
} 
