#include <iostream>

using namespace std;

bool isInt(float a){
    if (static_cast<int>(a) != a){
        return false;
    }
    else{
        return true;
    }
}

int tinhTongCacUocSo(int n){
    int Sum(0);

    for (int i = 1; i < n; i++){
        if (n % i == 0){
            Sum += i;
        }
    }

    return Sum;
}

int main(){
    float a_fl, b_fl;

    cout << "Nhap a (a > 0): ";
    cin >> a_fl;
    cout << "Nhap b (b > 0): ";
    cin >> b_fl;

    if (a_fl <= 0 || b_fl <= 0){
        cout << "Wrong input";
        return 0;
    }

    if (isInt(a_fl) == false || isInt(b_fl) == false){
        cout << "Hay nhap vao so nguyen";
        return 0;
    }

    int a = int(a_fl);
    int b = int(b_fl);
    int Sum_a = tinhTongCacUocSo(a);
    int Sum_b = tinhTongCacUocSo(b);

    cout << endl;
    
    if (Sum_a == b && Sum_b == a){
        cout << "1";
    }
    else{
        cout << "0";
    }

    return 0;
}