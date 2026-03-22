#include <iostream>
#include <cstring>
using namespace std;



struct Team{
    char name[40];
    int like;
    int comment;
    int share;
    int point = 0;

    // inline bool operator==(Team team){
    //     return like == team.like && comment == team.comment && share == team.share;
    // }
};

int getData(Team &team){
    cin.getline(team.name,40);
    int check = 0;
    for(int i = 0; i < 3; ++i)
        if (team.name[i] == '0') check++; 
    if (check == 3) return 0;

    cin >> team.like;
    cin >> team.comment;
    cin >> team.share;
    cin.ignore();
    return 1;
}

void outPut(Team teams[100], int n){
    for (int i = 0; i < n; i++){
        cout << teams[i].name << endl;
    }
}

int calPoint(Team &team){
    team.point = team.like + team.comment*2 + team.share*3;
    return team.point;
}

int rateTeam(Team teams[100],int n){
    int more = 0;
    for(int i = 0; i < n-1; ++ i){
        for(int j = i; j < n-i; ++j){
            if (calPoint(teams[i]) < calPoint(teams[j])){
                Team temp = teams[i];
                teams[i] =  teams[j];
                teams[j] = temp;
            }

        }
    }
    return more;
}

int main(){
    Team teams[100];
    int check = 1, idx = 0;
    do{
        check = getData(teams[idx++]);
    } while(check);

    int rate = rateTeam(teams, idx);
    
    outPut(teams, 3 + rate);
    return 0;
}