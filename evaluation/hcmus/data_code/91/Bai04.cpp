//kiem tra so ban be
#include <iostream>

using namespace std;

int tinhTongUoc(int n){
    int sum(0);
    for (int i = 1; i < n; i++){
        if (n % i == 0)
            sum += i;
    }
    return sum;
}

int main(){
    int a, b;
    cin >> a >> b;

    if (a < 0 || b < 0){
        cout << "Nhap sai";
        return 0;
    }

    if (tinhTongUoc(a) == b && tinhTongUoc(b) == a)
        cout << "1";
    else 
        cout << "0";

    return 0;
}