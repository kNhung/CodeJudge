#include <iostream>

using namespace std;

const int MAX = 100;
struct DoiTuyen{
    char name[MAX];
    int like;
    int comment;
    int share;
};

void input (DoiTuyen& a, int& n){
    for (int i = 0; i < n; i++){
        cout << "Name: ";
        cin >> a.name;

        cout << "Like: ";
        cin >> a.like;

        cout << "Comment: ";
        cin >> a.comment;

        cout << "Share: ";
        cin >> a.share;

        cout << endl;
    }
}

void output (DoiTuyen a, int n);
int main(){
    DoiTuyen a;
    int n;
    input(a, n);
    
    return 0;
}