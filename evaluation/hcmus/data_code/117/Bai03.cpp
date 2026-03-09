#include <iostream>
#include <cstring>
using namespace std;

struct Olympic {
    char name[40];
    int like;
    int cmt;
    int share;
};

void inputStruct(Olympic &a) {
    cin.getline(a.name, 40);
    cin >> a.like;
    cin >> a.cmt;
    cin >> a.share;
}

void inputArray (Olympic a[], int n) {
    for (int i = 0; i < n; i++) {
        inputStruct(a[i]);
    }
}

void printArray(Olympic a[], int n) {
    for (int i = 0; i < n; i++) {
        cout << "Name: " << a[i].name << endl;
        cout << "Like: " << a[i].like << endl;
        cout << "Comment: " << a[i].cmt << endl;
        cout << "Share: " << a[i].share << endl;
    }
}

void cpyStruct(Olympic &a,  Olympic &b) {
    strcpy(a.name, b.name);
    a.like = b.like;
    a.cmt = b.cmt;
    a.share = b.share;
}

void insertArray (Olympic a[], Olympic b, int pos) {
    for (int i = 4; i > pos; i--) {
        cpyStruct(a[i], a[i - 1]);
    }
    cpyStruct(a[pos], b);
}

void findWinner (Olympic a[], int n) {
    int arr[4];

    int first = 0;
    int second = 0;
    int third = 0;
    for (int i = 0; i < n; i++) {
        int score = a[i].like * 1 + a[i].cmt * 2 + a[i].share * 3;
        if (score > first) {
            arr[0] = i;
        }
    }
}
int main() {
    Olympic a[100];
    int n = 0;
    return 0;
}