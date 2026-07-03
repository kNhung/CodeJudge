#include <iostream>

using namespace std;

struct doituyen {
    char Name;
    int like;
    int Cmt;
    int Share;
};

void nhapdoituyen(doituyen team[]) {
    for (int i = 0; i != 0; i++) {
        cout << "Name :";
        cin >> team[i].Name;
        if (team[i].Name == 0) {
            break;
        }
        cout << "Like: ";
        cin >> team[i].like;
        cout << "Comment: ";
        cin >> team[i].Cmt;
        cout << "Share: ";
        cin >> team[i].Share;
        cout << endl;
    }
}

void sosanhdoituyen(doituyen team[]) {
    int diem = team[0].like + team[0].Cmt * 2 + team[0].Share * 3;
    int flag = -1;
    while () {

    }
}

int main() {
    
    nhapdoituyen();
}