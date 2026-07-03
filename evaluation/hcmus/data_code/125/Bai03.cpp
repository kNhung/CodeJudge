#include <iostream>
#include <cstring>

using namespace std;

struct Team{
    char name[40];
    int like;
    int comment;
    int share;
    int Diem;

    int input();
    void printName();
};

int Team::input(){
    cout << "Name: ";
    cin.getline(name, 100, '\n');

    if (name[0] == '0' && name[1] == '0' && name[2] == '0'){
        return 2;
    }

    cout << "Like: ";
    cin >> like;
    cout << "Comment: ";
    cin >> comment;
    cout << "Share: ";
    cin >> share;
    cin.ignore();
    cout << endl;

    if (like < 0 || share < 0 || comment < 0){
        return 0;
    }

    return 1;
}

void Team::printName(){
    for (int i = 0; i < strlen(name); i++){
        cout << name[i];
    }

    return;
}

int setArray(Team a[], int &n){
    int i(-1);
    while (true){
        i++;

        int check = a[i].input();

        if (check == 0){
            return 0;
        }
        else if (check == 2){
            return 1;
        }
    }

    n = i;

    return 1;
}

int timMax(Team a[], int n){
    int max = a[0].Diem;
    int pos;

    for (int i = 0; i < n; i++){
        if (max < a[i].Diem){
            max = a[i].Diem;
            pos = i;
        }
    }

    return pos;
}

void tinhDiem(Team a[], int n){
    for (int i = 0; i < n; i++){
        a[i].Diem = a[i].like + a[i].comment*2 + a[i].share*3;
    }
}

void xoaMax(Team a[], int &n, int pos){
    for (int i = pos; i < n; i++){
        a[i] = a[i + 1];
    }

    n--;
}

int main(){
    Team Doi[100];
    int n;

    int check = setArray(Doi, n);

    if (check == 0){
        cout << "Wrong input";
        return 0;
    }

    tinhDiem(Doi, n);
    int pos;
    for (int i = 1; i <= 3; i++){
        pos = timMax(Doi, n);
        Doi[pos].printName();
        cout << endl;
        xoaMax(Doi, n, pos);
    }





    return 0;
}