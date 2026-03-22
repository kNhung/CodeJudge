//tinh tong cac so chan trong khoang (a,b)
//input : a, b
//output: sum
#include <iostream>

using namespace std;

bool ktraSoChan(int a){
    if(a % 2 == 0)
        return true;
    else return false;
}

void tinhTongSoChan(int a, int b, int &sum){
    if(a > b)
        cout << "a phai be hon b. Nhap lai!";
    else{
        for( ; a <= b; ++a){
            if(ktraSoChan(a) == true)
                sum += a;
            
        }
    }
}

int main(){
    int a, b;
    int sum = 0;

    cin >> a >> b;

    tinhTongSoChan(a, b, sum);
    cout << "Tong cac so chan trong khoang " << a << "den " << b << ": " << sum;
    return 0;
}