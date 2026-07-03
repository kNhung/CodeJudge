#include <iostream>
#include <cstring>
using namespace std;

void deleteAt(char s[], int pos){
    int n = strlen(s);
    for(int i = pos; i <= n; i++){
        s[i] = s[i + 1];
    }
}

bool checkLienTiep(char s[]){
    int n = strlen(s);
    for(int i = 0; i < n - 1; i++){
        if(s[i] == s[i + 1]) return false;
    }
    return true;
}

void xoaTrungLap(char s[]){
    int n = strlen(s);
    int i = 0;
    int count = 0;
    while(s[i] != '\0'){
        if(s[i] == s[i + 1]){
            int k = i;
            while(s[k] != s[k + 1]){
                count++;
                k++;
            }
            count += 2;
        }
        if(count != 0){
            while(count != 0){
                deleteAt(s, i);
                count--;
            }
        } else i++;
    }
}

int main(){
    char s[100];
    
    cin.getline(s, 100);
    while(!checkLienTiep(s)){
        xoaTrungLap(s);
    }
    cout << s;
    return 0;
}