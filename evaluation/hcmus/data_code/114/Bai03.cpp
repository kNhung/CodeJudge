#include <iostream>
#include <cstring>

using namespace std;

struct Team{
    char Name[40];
    int Like;
    int Comment;
    int Share;  
};

void input(Team team[], int& n){
    for(int i = 0; i < n; i++){
        cout << "Nhap thong tin doi thu " << i + 1 << ":\n";
        cout << "Nhap ten doi: ";
        cin.ignore();
        cin.getline(team[i].Name, 40);
        cout << "Nhap so luot like: ";
        cin >> team[i].Like;
        cout << "Nhap so luot comment: ";
        cin >> team[i].Comment;
        cout << "Nhap so luot share: ";
        cin >> team[i].Share;
    }
}

void print(Team team[], int& n){
    for(int i = 0; i < n; i++){
        cout << "Doi thu " << i + 1 << ":\n";
        cout << "Ten doi: " << team[i].Name << endl;
        cout << "So luot like: " << team[i].Like << endl;
        cout << "So luot comment: " << team[i].Comment << endl;
        cout << "So luot share: " << team[i].Share << endl;
        cout << "--------------------------------------------------\n";
    }
}

void compare(Team team[], int& n){
    int first = 0;
    int second = 0;
    int third = 0;
    int sharemax;
    int likemax;
    int commentmax;

    for(int i = 0; i < n; i++){

        int point = team[i].Like + team[i].Comment * 2 + team[i].Share * 3;

        if(point > first)
            first = point;

    }

    for(int i = 0; i < n; i++){

        int point = team[i].Like + team[i].Comment * 2 + team[i].Share * 3;
            if(point < first && point > second)
                second = point;

    }

    for(int i = 0; i < n; i++){

        int point = team[i].Like + team[i].Comment * 2 + team[i].Share * 3;

        if(point < first && point < second && point > third)
            third = point;
        
    }

    for(int j = 0; j < n; j++){

        int point = team[j].Like + team[j].Comment * 2 + team[j].Share * 3;

        if(point == first && team[j].Share ){
            cout << "Doi dung thu nhat la:\n";
            cout << "Ten doi: " << team[j].Name << endl;
            cout << "------------------------------------------\n";
        }
    }
    for(int j = 0; j < n; j++){

        int point = team[j].Like + team[j].Comment * 2 + team[j].Share * 3;

        if(point == second){
            cout << "Doi dung thu hai la:\n";
            cout << "Ten doi: " << team[j].Name << endl;
            cout << "------------------------------------------\n";
        }
    }

    for(int j = 0; j < n; j++){

        int point = team[j].Like + team[j].Comment * 2 + team[j].Share * 3;

        if(point == third){
            cout << "Doi dung thu ba la:\n";
            cout << "Ten doi: " << team[j].Name << endl;
            cout << "------------------------------------------\n";
        }
    }
}

int main(){
    Team team[100];
    int n;

    cout << "Nhap so doi thi: ";
    cin >> n;

    if(n <= 0)
        cout << "Nhap sai";

    input(team, n);
    print(team, n);
    cout << "------------------------------------------------\n";
    compare(team, n);
}