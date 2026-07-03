#include <iostream>
#include <cstring>
#include <cmath>
using namespace std;
struct Team{
    char name[100];
    int like, comment, share;
};
int dem = 3;
void sapxep(Team a[], int n){
    for(int i = 0; i < n; i++){
        int max_index = i;
        int totala = a[i].like + a[i].comment * 2 + a[i].share * 3;
        for(int j = i + 1; j < n; j++){
            int totalb = a[j].like + a[j].comment * 2 + a[j].share * 3;
            if(totala < totalb){
                totala = totalb;
                max_index = j;
            }
            else if(totala == totalb){
                dem++;
                Team tmp = a[i + 1];
                a[i + 1] = a[max_index];
                a[max_index] = tmp;
            }
        }
        Team tmp = a[i];
        a[i] = a[max_index];
        a[max_index] = tmp;
    }
}
int main(){
    Team a[1000];
    int n = 0;
    int k = 1;
    while(k != 0){
        char c[1000];
        cout << "Name: ";
        cin.getline(c, 1000);
        if(strcmp(c, "000") == 0){
            k = atoi(0);
            break;
        }
        strcpy(a[n].name, c);
        cout << "Like: ";
        cin >> a[n].like;
        cout << "Comment: ";
        cin >> a[n].comment;
        cout << "Share: ";
        cin >> a[n].share;
        cin.ignore();
        cout << endl;
        n++;
    }
    sapxep(a, n);
    for(int i = 0; i < 3; i++){
        cout << a[i].name << endl;
    }
}