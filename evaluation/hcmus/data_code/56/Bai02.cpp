#include <iostream>
#include <cmath>
using namespace std;

int count(int n){
    int count = 0, d;
    while(n != 0){
        d = d % 10;
        n = n / 10;
        count++;
    }

    return count;
}

bool isAutomorphic(int n, int count){
    if(n < 0){
        cout << "error";
    } else {
        int d;
        d = (n * n) % int(pow(10, count));
        if (n - d == 0) return true;
    }

    return false;
}

int main(){
    int n;

    cin >> n;

    cout << isAutomorphic(n, count(n));

    return 0;
}