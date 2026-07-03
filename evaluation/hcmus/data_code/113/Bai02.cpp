#include <iostream>
#include <cstring>
using namespace std;
void removeDuplicates(char s[]) {
    int length = strlen(s);
    if (length < 2)
        return;

    int currentIndex = 1;
    for (int i = 1; i < length; i++) {
        if (s[i] != s[i - 1]) {
            s[currentIndex] = s[i];
            currentIndex++;
        }
    }

    s[currentIndex] = '\0';  // Ket thuc chuoi moi sau khi xoa cac ki tu trung lap//
}

int main() {
    char s[100];
    cin >> s;
    removeDuplicates(s);

    cout << s << endl;

    return 0;
}