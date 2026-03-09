#include <iostream>
#include <math.h>
using namespace std;
int uoc(int n){
    int sum = 0;
    for(int i = 1; i <= sqrt(n); i++){
        if(n % i == 0){
            sum += i + n / i;
        }
        if(i == sqrt(n)){
            sum -= i;
        }
    }
    return sum - n;
}
int main(){
    int a, b;
    cin >> a >> b;
    if(uoc(a) == b && uoc(b) == a){
        cout << 1 << endl;
    }
    else cout << 0 << endl;
    return 0;
}