#include <iostream>
#include <cstring>
using namespace std;

void delChar(char s[]){
    int check = 1;
    int len = strlen(s);
    do{
        int pos = 0;
        for(int i = 0; i < len-1; ++i){
            if (s[i] == s[i+1]){
                check++;
                pos = i;
            }
        }

        for (int i = pos; i < len - 2; ++i){
            s[i] = s[i+2];
            cout << s << endl << endl;
        }
    len -= 2;
    check--;
    } while (check);
    s[len+2] = 0;
}

int main(){
    char s[100];
    cin >> s;
    delChar(s);
    cout << s;
    return 0;

}