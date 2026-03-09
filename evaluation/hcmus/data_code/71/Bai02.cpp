#include<iostream>
#include<cmath>
using namespace std;

void Nhap(int &n){
    cin >> n;
    while(n <= 0){
        cin >> n;
    }
    return;
}


int CheckNum(int n){
    int tmp = pow(n,2);
    for(int i = 10; i <= tmp; i *= 10){
        if(tmp % i == n) return 1;
    }
    return 0;
}

int main(){
    int n(0);
    Nhap(n);
    cout << CheckNum(n);
    return 0;
}