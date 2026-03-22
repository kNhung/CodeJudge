#include <iostream>

using namespace std;

int main(){
    int n;
    cin >> n;

    int automorphic = n*n;
    while (n>0){
        if (automorphic % 10 != n % 10){
            cout << 0;
            return 0;
        }
        automorphic /= 10;
        n /= 10;
    }
    cout << 1;

    return 0;
}