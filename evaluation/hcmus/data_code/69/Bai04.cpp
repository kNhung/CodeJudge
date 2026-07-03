#include <iostream>

using namespace std;

int tongUS(int n){
    int sum = 0;
    for (int i = 1; i <= n/2; ++ i){
        if(n % i == 0)
            sum += i;
    }
    return sum;
}

int main(){
    int n1, n2;
    cin >> n1 >> n2;

    if (n1 == tongUS(n2) && n2 == tongUS(n1))
        cout << 1;
    else
        cout << 0;

    return 0;
}