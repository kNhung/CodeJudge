#include <iostream>
#include <cstring>
#include <cmath>
using namespace std;

#define MAX 100
#define MAX_NAME 40
struct Doi{
    char ten[MAX_NAME];
    int like;
    int cmt;
    int share;
};

void doiDoi(Doi &doi1, Doi &doi2) {
    Doi temp = doi1;
    doi1 = doi2;
    doi2=temp;
}

void locDoi (Doi doi[], int soDoi) {
    for (int i = 0; i < soDoi - 1; i++) {
        for (int j = 0; j < soDoi - i - 1; j++) {
            if (doi[j].like < doi[j + 1].like) {
                doiDoi(doi[j], doi[j + 1]);
            }
        }
    }
}

void xuat(Doi doi[], int soDoi, int soDoiManhNhat) {
    cout << soDoiManhNhat <<endl;
    for(int i = 0; i < soDoiManhNhat; i++) {
        cout << doi[i].ten << endl;
    }
}





int main() {
    Doi teams[MAX_NAME];
    int soDoi = 0;


    return 0;
}
