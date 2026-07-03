//tinh tong cac so chan tu a den b
#include <iostream>

using namespace std;

//kiem tra so chan
bool checkSoChan(int n){
    if (n % 2 == 0)
        return 1;
    else
        return 0;
}

int main(){
    int a, b;
    int sum(0);
    cin >> a >> b;

    if (a <= b){
    for (int i = a; i <= b; i++){
        if (checkSoChan(i))
            sum+= i;
    }
    cout << sum;
    }
    else   
        cout << "Nhap sai";
    return 0;
}