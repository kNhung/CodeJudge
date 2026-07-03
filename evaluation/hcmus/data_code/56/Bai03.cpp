#include <iostream>
#include <cmath>
using namespace std;

int count1(int n){
    int count = 0, d;
    while(n != 0){
        d = d % 10;
        n = n / 10;
        count++;
    }

    return count;
}

bool doiXung(int n){
    int d, reverse = 0, temp = n;

    while(temp != 0){
        d = temp % 10;
        temp = temp / 10;
        reverse = reverse * 10 + d;
    }

    if(reverse == n) return true;
    else return false;
}

int laySo(int n, int vitri){
    return (n % int(pow(10, vitri)) / (pow(10, vitri - 1)));
}

int suaDoiXung(int n){
    if(doiXung(n)) return n;
    else {
        int a, b, d;
        while (!doiXung(n)){
        for(int i = 1; i <= count1(n); i++){
            a = laySo(n, i);
            b = laySo(n, n + 1 - i);
            if (a == b) continue;
            else if (a > b){
                d = n % (int(pow(10, n - i)));
                n = n / (int(pow(10, n - i + 1)));
                n = n * int(pow(10, n - i)) + d;
            } else {
                int temp = n;
                d = n % (int(pow(10, i - 1)));
                n = n / (int(pow(10, i)));
                n = n * int(pow(10, i - 1)) + d; 
            }
        }
        }
        return n;
    }
}

int main(){
    int n;

    cin >> n;

    if (n >= 1000 && n <= 9999){
        cout << suaDoiXung(n);
    } else{
        cout << "error input";
    }

    return 0;
}