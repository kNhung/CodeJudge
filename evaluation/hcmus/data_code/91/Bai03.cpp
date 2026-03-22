#include <iostream>
#include <cmath>

using namespace std;

//ktra so doi xung
bool checkSoDoiXung(int n){
    int temp, m(0);
    int tempN = n;
    while (n != 0){
        m *= 10;
        temp = n % 10;
        m += temp;
        n /= 10;
    }

    if (tempN == m)
        return 1;
    else 
        return 0;
}

int main(){
    int n;
    cin >> n;

    if (n < 1000 || n > 9999){
        cout << "Nhap sai";
        return 0;
    }

    int n1 = n;
    //xoa so
    int d;
    int right;
    int left;
    int num;

    if (checkSoDoiXung(n)){
        cout << n;
        return 0;
    }

    int max = 0;
    int max1 = 0;

    for(int i = 1;n > pow(10,i) ; i++){
        for (int j = i; n > pow(10,j) ;j++){
            d = n % (int)pow(10, j - 1);
            left = d % (int)pow(10, j - 2);
            right /= pow(10,j);
            num = right*10 + left;

            if (checkSoDoiXung(num)){
                if (num > max)
                    max = num;
            }
            if (max > max1)
                max1 = max;
        }
    }

    cout << max1;
    return 0;
}