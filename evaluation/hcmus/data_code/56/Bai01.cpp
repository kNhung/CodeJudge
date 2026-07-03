#include <iostream>

using namespace std;

int sum(int a, int b){
    int sum = 0;

    if(a > b){
        cout << "error";
    } else {
        while (a <= b) {
            if (a % 2 == 0) sum = sum + a;
            a++;
        }
    }

    return sum;
}

int main(){
    int a, b;

    cin >> a >> b;

    cout << sum(a, b);

    return 0;
}