#include <iostream>
#include <cstring>
using namespace std;

const int MAX = 100;

void inputStr (char a[], int& n){
    cin >> a;
    n = strlen(a);
}

void outputStr (char a[], int n){
    for (int i = 0; i < n; i++)
        cout << a[i];
}

void xoa2thanhPhan (char a[], int& n, int pos){
    for (int i = pos; i < n - 2; i++)
        a[i] = a[i + 2];
    n -= 2;
}
void xoaKiTu(char a[], int& n){
    for (int i = 0; i < n; i++)
        while (a[i] == a[i + 1])
            xoa2thanhPhan(a, n, i);  
}

int main (){
    char str[MAX];
    int n;
    inputStr(str, n);
    xoaKiTu(str, n);
    outputStr(str, n);
    return 0;
}
