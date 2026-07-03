#include <iostream>
#include <math.h>
using namespace std;
bool check(int n){
    int automorphic = 0;
    long long m = pow(n, 2);
    for(int i = 1; m!= 1 ; i*=10){
        automorphic += i * (m % 10) ;
        m /= 10;
        if(automorphic == n){
            return true;
        }
    }
    return false;
}
int main(){
    int n;
    cin >> n;
    cout << check(n) << endl;
    return 0;
}