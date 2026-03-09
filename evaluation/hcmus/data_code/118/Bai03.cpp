#include<iostream>
#include<cstring>
using namespace std;

struct Doi{
    char Name[50];
    int Like;
    int Comment;
    int Share;

    void input();
    void output();
};

void Doi:: input(){
    cin.getline(Name,50,'\n');
    cin.ignore();
    cin >> Like;
    cin >> Comment;
    cin >> Share;

}


void inputArr(Doi a[]){
    int i = 0;
    cout << "Doi: ";
    while(true){
        a[i].input();
        if(strcmp(a[i].Name,"000") == 0) return;
        cout << "Doi: " << endl;
    }
}

int main(){
    Doi a[50];
    inputArr(a);
    return 0;
}