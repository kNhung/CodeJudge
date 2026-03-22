#include <iostream>
#include <cstring>
using namespace std;

struct Doi {
    char name[40];
    int like, comment, share;
};

void input(Doi d[], int& n){
    int count = 0;

    while(true){
        cout << "name: ";
        cin.getline(d[n].name, 40);
        for(int j = 0; j < 3; j++){
            if(d[n].name[j] == '0') count++;
        }
        if(count == 3) break;
        cout << "like: ";
        cin >> d[n].like;
        cout << "comment: ";
        cin >> d[n].comment;
        cout << "share: ";
        cin >> d[n].share;
        n++;
        cin.ignore();
    }
}

int tinhDiem(Doi d){
    return d.like + 2 * d.comment + 3 * d.share;
}

void output(Doi d[], int n){
    int max = -1, second = -1, third = -1;
    int max_score = -1, second_score = -1, third_score = -1;

    for(int i = 0; i < n; i++){
        if(tinhDiem(d[i]) > max_score){
            max_score = tinhDiem(d[i]);
            max = i;
        }
    }

    for(int i = 0; i < n; i++){
        if(tinhDiem(d[i]) > second_score && tinhDiem(d[i]) < max_score){
            second_score = tinhDiem(d[i]);
            second = i;
        }
    }

    for(int i = 0; i < n; i++){
        if(tinhDiem(d[i]) > third_score && tinhDiem(d[i]) < second_score){
            third_score = tinhDiem(d[i]);
            third = i;
        }
    }

    cout << d[max].name << endl;
    cout << d[second].name << endl;
    cout << d[third].name << endl;
}

int main(){
    Doi d[100];
    int n = 0;

    input(d, n);
    output(d, n);

    return 0;
}