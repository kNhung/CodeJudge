/*
    Ta Xuan Truong _ 23127506
*/

#include <iostream>
#include <cstring>

using namespace std;

const int MAXNUM = 1000;
/*
    01234
    abcdef
    cdefef
*/
void deleteChar(char s[MAXNUM], int pos1, int pos2){
    int i = 0;
    while (i + pos2 < strlen(s)){
        s[i+pos1] = s[i+pos2];
        i ++; 
    }
    s[strlen(s)-(pos2-pos1)] = 0;
}

void deleteDuplicate(char s[MAXNUM])
{
    int temp = 0, i = 0;
    while (i < strlen(s)){
        if (s[i] == s[i+1]){
            int temp = i;
            i ++;
            while(s[i] == s[i-1])
                i ++;
            i --;
            deleteChar(s, temp, i+1);
            i = 0;
        }
        else 
            i ++;
    }
}

int main()
{
    char s[MAXNUM] = "abcdef";
    cin.getline(s, MAXNUM - 1);
    deleteDuplicate(s);    
    cout << s;
    return 0;
}