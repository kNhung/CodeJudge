#include <iostream>
#include <cstring>
#include <cmath>
using namespace std;
bool check(char s[]){
    for(int i = 1; i < strlen(s); i++){
        if(s[i] == s[i - 1]){
            return false;
        }
    }
    return true;
}
void delete_char(char s[], int length, int k){
    for(int i = k; i < strlen(s) - length; i++){
        s[i] = s[i + length];
    }
    s -= length;
}
int main(){
    char s[1000];
    cin >> s;
    while(!check(s)){
        for(int i = 0; i < strlen(s) - 1; i++){
            if(s[i] == s[i + 1]){
                int dem = 1;
                int k = i;
                while(s[i] == s[i + 1]){
                    dem++;
                    i++;
                }
                delete_char(s, dem, k);
                i -= dem;
            }
        }
    }
    cout << s;
}