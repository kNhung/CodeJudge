#include <iostream>
using namespace std;
#include<cstring>
const int MAX_NAME_LENGTH = 100;
const int MAX_TEAMS = 5;

struct Team {
    char name[MAX_NAME_LENGTH];
    int like;
    int comment;
    int share;
    int score;
};

void sortTeams(Team teams[], int numTeams) {
    for (int i = 0; i < numTeams - 1; i++) {
        for (int j = i + 1; j < numTeams; j++) {
            if (teams[j].score > teams[i].score ||
                (teams[j].score == teams[i].score && teams[j].share > teams[i].share) ||
                (teams[j].score == teams[i].score && teams[j].share == teams[i].share && teams[j].comment > teams[i].comment) ||
                (teams[j].score == teams[i].score && teams[j].share == teams[i].share && teams[j].comment == teams[i].comment && teams[j].like > teams[i].like)) {
                Team temp = teams[i];
                teams[i] = teams[j];
                teams[j] = temp;
            }
        }
    }
}

int main() {
    Team teams[MAX_TEAMS];

    int numTeams = 0;

    for (int i = 0; i < MAX_TEAMS; i++) {
        cout << "Name: ";
        cin.getline(teams[i].name, MAX_NAME_LENGTH);

        if (teams[i].name[0] == '0' && teams[i].name[1] == '0' && teams[i].name[2] == '0')
            break;

        cout << "Like: ";
        cin >> teams[i].like;
        cout << "Comment: ";
        cin >> teams[i].comment;
        cout << "Share: ";
        cin >> teams[i].share;
        cin.ignore();  

        teams[i].score = teams[i].like + 2 * teams[i].comment + 3 * teams[i].share;

        numTeams++;
    }

    sortTeams(teams, numTeams);

    int numWinners = std::min(3, numTeams);

    for (int i = 0; i < numWinners; i++) {
        cout << teams[i].name << endl;
    }

    return 0;
}