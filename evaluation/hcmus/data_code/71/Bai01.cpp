#include<iostream>
using namespace std;

int main(){
    int a(0), b(0), DapAn(0);
    cin >> a;
    cin >> b;
    for(int i = a; i <= b; ++i){
        if(i % 2 == 0){
            DapAn += i;
        }
    }
    cout << "Output: " << DapAn;
    return 0;
}