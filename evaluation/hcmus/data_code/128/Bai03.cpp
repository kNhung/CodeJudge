#include <iostream>
using namespace std;
#define MAX 40
#define MAXTEAM 100
struct TEAMS {
    char name[MAX];
    int like;
    int comment;
    int share;
    void input(){}
    int point;
    

};

void TEAMS::input() {
cin.ignore();
cout << "Name: ";
cin.getline(name, 40);
cout << "Like: ";
cin >> like;
cout << "Comment: ";
cin >> comment;
cout << "Share: ";
cin >> share;
}

void inputList(struct Team[MAXTEAM], int &n){
    cout << "So luong team:";
    cin >> n;

    for (int i = 0; i < n ; i++) {
        cout << "* Team " << i + 1 << endl;
        Team[i].input;
    }
}

void Point (struct Team[], int n) {
    int Max1 = -1;
    int Max2 = -1, Max3 =-1;

    for (int i = 0; i < n ; i++) {
        Team[i].point =  Team[i].like +  Team[i].comment * 2 + Team[i].share * 3;
        if (Team[i].point > Max1) {
            Max1 = Max2;
            Max2 = Max3;
            Max1 = Team[i].point;
            break;
        }
        else if (Team[i].point > Max2) {
            Max2 = Max3;
            Max2 = Team[i].point;
            break;
        }
        else if (Team[i].point > Max3) {
            Max3 = Team[i].point;
        }
    }
}

int main() {
    int n;
    struct Team[MAXTEAM];

    inputList (Team, n);
    Point(Team, n);
}