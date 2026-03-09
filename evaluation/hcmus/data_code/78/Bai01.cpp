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

int main(){
    float a_fl, b_fl;

    cout << "Nhap a: ";
    cin >> a_fl;
    cout << "Nhap b: ";
    cin >> b_fl;

    if (a_fl > b_fl){
        cout << "Wrong input";
        return 0;
    }

    if (isInt(a_fl) == false || isInt(b_fl) == false){
        cout << "Hay nhap vao so nguyen";
        return 0;
    }

    int a = int(a_fl);
    int b = int(b_fl);
    int Sum(0);

    for (int i = a; i <= b; i++){
        if (i % 2 == 0){
            Sum += i;
        }
    }

    cout << endl;
    cout << Sum;

    return 0;
}