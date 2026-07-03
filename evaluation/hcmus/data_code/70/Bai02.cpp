#include <iostream>

using namespace std;

int solve(int n){
    int square = n * n;
    int numDigit = 1;
    int tmp = square - n;
    int tmp1 = n;
    while (tmp1 != 0) {
        numDigit *= 1;
        tmp1 /= 10;
    }

    if ((tmp % numDigit) == 0) {
        return 1;
    }

    return 0;
}

int main() {
    int n;
    cin >> n;

    cout << solve(n);
    return 0;
}