#include <iostream>
#include <cstring>

using namespace std;

void xoaTrung(char str[]) {
    int len = strlen(str);
    int i = 0;

    while (i < len - 1) {
        if (str[i] == str[i + 1]) {
            for (int j = i; j < len; j++) {
                str[j] = str[j + 2];
            }
            len = len - 2;
            i--;
        }
        else {
            i++;
        }
    }
}

int main() {
    char str[1000];
    cin.getline(str, 1000);

    xoaTrung(str);

    cout << str << endl;

    return 0;
}