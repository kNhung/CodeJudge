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

int demChuSo(int n){
    int count(0);

    while (n != 0){
        n /= 10;
        count++;
    }

    return count;
}

int pow10(int n){
    int pow(1);

    for (int i = 1; i <= n; i++){
        pow *= 10;
    }

    return pow;
}

int main(){
    float n_fl;

    cout << "Nhap vao so nguyen duong n (n > 0): ";
    cin >> n_fl;

    if (n_fl <= 0){
        cout << "Wrong input";
        return 0;
    }

    if (isInt(n_fl) == false){
        cout << "Hay nhap vao so nguyen";
        return 0;
    }

    int n = int(n_fl);
    int SquareN = n*n;
    int count = demChuSo(n);

    cout << endl;
    
    if (SquareN % pow10(count) == n){
        cout << "1";
    }
    else{
        cout << "0";
    }

    return 0;
}