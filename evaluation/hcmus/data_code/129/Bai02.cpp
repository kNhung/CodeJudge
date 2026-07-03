#include <iostream>
#include <cstring>

using namespace std;

void inputS(char s[]){
    cout << "Nhap chuoi chu cai: ";
    cin.getline(s, 1000);
}

void xoaChu(char s[], int len, int x){
    for(int i = x; i < len; i++){
        s[i] = s[i + 2];
    }
}

void vongLap(char s[]){
    int len = strlen(s);
    for(int i = 0; i < len; i++){
        if(s[i] == s[i+1]){
            xoaChu(s, len, i);
            i = -1;
        }
    }
}

int main(){
    char s[1000];

    
    return 0;
}