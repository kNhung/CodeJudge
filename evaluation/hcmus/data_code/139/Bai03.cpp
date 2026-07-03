/*
    Ta Xuan Truong _ 23127506
*/

#include <iostream>
#include <cstring>

using namespace std;

const int MAXNUM = 1000;

struct team{
    int like, com, share, point;
    char name[41];
    void input();
};

void inputArr(team list[MAXNUM], int &n)
{
    n = 0;
    while(true){
        list[n].input();
        if (list[n].point == -1)
            return;
        n++;
        cout << '\n';
        cin.ignore(1);
    }
}

void swapint(int &a, int &b)
{
    int temp = a;
    a = b;
    b = temp;
}

void swapTeam(team &a, team&b){
    char temp[41];
    strcpy(temp, a.name );
    strcpy(a.name, b.name);
    strcpy(b.name, temp);
    swap(a.com, b.com);
    swap(a.like, b.like);
    swap(a.share, b.share);
    swap(a.point, b.point);
}

void sortArr(team list[MAXNUM], int &n)
{
    for (int i = 0; i < n-1; i++){
        int temp = i;
        for (int j = i+1; j < n; j++)
            if (list[temp].point >  list[j].point)
                temp = j;
        swapTeam(list[temp], list[i]);
    }
}

void outputArr(team list[MAXNUM], int n, int start)
{
    for (int i = start; i < n; i++)
        cout << list[i].name << '\n';
}
int main()
{
    team list[MAXNUM];
    int n;
    inputArr(list, n);
    sortArr(list, n);
    if (n <= 3)
        outputArr(list, n, 0);
    else
        outputArr(list, n, n-3);
    return 0;
}

void team::input()
{
    cout << "Name: ";
    cin.getline(name, 40);
    if (name[0] == '0' && name[1] == '0' && name[2] == '0'){
        point = -1;
        return ; 
    }
    cout << "Like: ";
    cin >> like;
    cout << "Comment: ";
    cin >> com;
    cout << "Share: ";
    cin >> share;
    point = like + com*2 + share*3;

}