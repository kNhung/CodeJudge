/*
Ho ten: Le Nguyen Nhat Truong
Lop: 23CLC02
MSSV: 23127136

Chuong trinh: xoa cac ki tu trung lap lien tiep
*/

#include <iostream>
#include <cstring>

using namespace std;

const int MAX_LEN = 256;

void deleteCharFrom(char s[], int pos, int numChar) {
    int len = strlen(s);
    for (int i = pos; s[i + numChar] != '\0'; i++) {
        s[i] = s[i + numChar];
    }
    s[len - numChar] = '\0';
}

void xoaKiTuTrungLap(char s[]) {
    bool xoaXong = false;
    while (!xoaXong) {
        xoaXong = true;
        for (int i = 1; s[i] != '\0'; i++) {
            if (s[i] == s[i - 1]) {
                deleteCharFrom(s, i - 1, 2);
                xoaXong = false;
            }
        }
    }
}

int main() {
    char s[MAX_LEN];
    cin.getline(s, MAX_LEN);

    xoaKiTuTrungLap(s);

    cout << s;

    return 0;
}