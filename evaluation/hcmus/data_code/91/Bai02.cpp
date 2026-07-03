//kiem tra so automorphic
#include <iostream>
#include <cmath>

using namespace std;

//check so chu so
int checkSoChuSo(int n){
    int count = 0;
    while (n != 0){
        n /= 10;
        count++;
    }
    return count;
}


int main(){
    int n;
    cin >> n;

    if (n > 0){
        int n2 = n*n;
        int soChuSo = checkSoChuSo(n);
        int pow10 = pow(10,soChuSo);
        
        if ((n2 % pow10 ) == n)
            cout << "1";
        else
            cout << "0";
        }
    else
        cout << "Nhap sai";
    return 0;
}