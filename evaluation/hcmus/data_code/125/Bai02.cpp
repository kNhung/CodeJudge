#include <iostream>
#include <cstring>

using namespace std;

int timViTri(char s[]){
    int pos;

    for (int i = 0; i < strlen(s); i++){
        if (s[i] == s[i + 1]){
            pos = i;
            return pos;
        }
    }

    return -1;
}

int demChuTrungNhauLienTiep(char s[], int &pos){
    int count(1);
    pos = timViTri(s);

    if (pos == -1){
        return 0;
    }

    for (int i = pos; i < strlen(s); i++){
        if (s[i] != s[i + 1]){
            break;
        }

        count++;
    }

    return count;
}

void xoaChuCaiTrungNhau(char s[]){
    int pos;

    while(true){
        int count = demChuTrungNhauLienTiep(s, pos);

        if (count == 0){
            break;
        }

        for (int i = 1; i <= count; i++){
            for (int j = pos; j < strlen(s); j++){
                s[j] = s[j + 1];
            }
        }

        s[strlen(s)] = '\0';
    }
}

void printString(char s[]){
    for (int i = 0; i < strlen(s); i++){
        cout << s[i];
    }

    return;
}

int main(){
    char s[100];

    cin >> s;

    xoaChuCaiTrungNhau(s);
    cout << endl;
    printString(s);

    return 0;
}