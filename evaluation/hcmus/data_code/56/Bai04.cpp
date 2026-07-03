#include <iostream>
#include <cmath>
using namespace std;

int tongUoc(int n){
    int sum = 0;
    for(int i = 1; i < n; i++){
        if(n % i == 0) sum = sum + i;
    }
    return sum;
}

bool isFriend(int a, int b){
    if(tongUoc(a) == b && tongUoc(b) == a) return true;
    return false;
}

int main(){
    int a, b;

    cin >> a >> b;

    cout << isFriend(a, b);

    return 0;
}