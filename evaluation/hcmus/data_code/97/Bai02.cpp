#include <iostream>
#include <cstring>

using namespace std;

void remove(char* s) {
    int len = strlen(s);
    int index = 0;

    for (int i = 0; i < len; ++i) {
        if (index == 0 || s[i] != s[index - 1]) {
            s[index++] = s[i];
        }
        else {
            index--;
        }
    }

    s[index] = '\0';
}

int main() {
    char inputStr[] = "abbaca";
    remove(inputStr);
    cout << inputStr << endl;

    return 0;
}
