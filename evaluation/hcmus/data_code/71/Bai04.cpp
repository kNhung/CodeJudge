#include<iostream>
using namespace std;

void Nhap(int &a, int &b){
    cin >> a >> b;
    while(a <= 0 || b <= 0){
        cin >> a >> b;
    }
    return;
    
}

bool CheckSoBB(int a, int b){
    int TongUoca = 0;
    int TongUocb = 0;
    for(int i = 1; i < a; ++i){
        if(a % i == 0){
            TongUoca += i;
        }
    }

    for(int i = 1; i < b; ++i){
        if(b % i == 0){
            TongUocb += i;
        }
    }

    if(TongUoca == b && TongUocb == a) return true;
    else return false;
}

int main(){
    int a(0), b(0);
    Nhap(a,b);
    cout << CheckSoBB(a,b);
    return 0;
}