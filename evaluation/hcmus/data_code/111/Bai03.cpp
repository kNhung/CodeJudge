/*
Ho ten: Le Nguyen Nhat Truong
Lop: 23CLC02
MSSV: 23127136

Chuong trinh: 
*/

#include <iostream>
#include <cstring>

using namespace std;

const int MAX_MEM = 30;

struct DoiTuyen {
    char ten[40];
    int like;       //1 like = 1 diem
    int cmt;        //1 comment = 2 diem
    int share;      //1 share = 3 diem
    int tongDiem;
};

//Ham so sanh su giong nhau hoan toan cua hai chuoi dua vao 
bool compareCharArr(char s[], char cmp[]) {
    if (strlen(cmp) > strlen(s)) return false;
    for (int i = 0; s[i] != '\0'; i++) {
        if (s[i] != cmp[i]) return false;
    }
    return true;
}

void inputDoiTuyen(DoiTuyen dt[], int& n) {
    char end[] = "000";
    for (int i = 0; i < MAX_MEM; i++) {
        cout << "Name: ";
        cin >> dt[i].ten;
        if (compareCharArr(dt[i].ten, end)) return ;

        cout << "Like: ";
        cin >> dt[i].like;

        cout << "Comment: ";
        cin >> dt[i].cmt;

        cout << "Share: ";
        cin >> dt[i].share;

        dt[i].tongDiem = dt[i].like + (2 * dt[i].cmt) + (3 * dt[i].share);
        n++;
        cout << endl;
    }
}

void outputXepHang(DoiTuyen dt[], int n) {
    int rank[n], highestRank = 0;
    int currentMax = dt[0].tongDiem;   
    int currentMin = dt[0].tongDiem;

    rank[0] = 0;
    for (int i = 1; i < n; i++) {
        if (dt[i].tongDiem > currentMax) {
            currentMax = dt[i].tongDiem;
            rank[i] = ++highestRank;
        }
        else if (dt[i].tongDiem == currentMax) {
            rank[i] = highestRank;
        }
        else if (dt[i].tongDiem < currentMax && dt[i].tongDiem > currentMin) {
            rank[i] = highestRank;
            for (int j = 0; j < i; j++) rank[j]++;
        }
        else if (dt[i].tongDiem < currentMin) {
            currentMin = dt[i].tongDiem;
            rank[i] = 0;
            for (int j = 0; j < i; j++) rank[j]++;
        }
        else if (dt[i].tongDiem == currentMin) {
            rank[i] = 0;
        }
    }

    for (int count = 0; count < 3; count++) {
        for (int i = n - 1; i >= 0; i--) {
            if (rank[i] == highestRank)
                cout << dt[i].ten << '\n';
        }
        highestRank--;
    }
}

int main() {
    DoiTuyen dt[MAX_MEM];
    int soDoi(0);
    
    inputDoiTuyen(dt, soDoi);
    outputXepHang(dt, soDoi);
    
    return 0;
}