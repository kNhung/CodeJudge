#include <iostream>
using namespace std;

bool isAutomorphic(int n) {
    int square = n*n;
    int nDigits = 0;
    int squareDigits = 0;

    int temp = n;
    while (temp != 0) {
        temp /= 10;
        nDigits++;
    }

    temp = square;
    while (temp != 0) {
        temp /= 10;
        squareDigits++;
    }

    int div = 1;
    for (int i = 0; i < nDigits; i++) {
        div *= 10;
    }

    return (square % div == n);
}

int main() {
    int n;
    cout << "Input n (n>0): ";
    cin >> n;

    if (isAutomorphic(n)) {
        cout << "1" << endl;
    } else {
        cout << "0" << endl;
    }

    return 0;
}