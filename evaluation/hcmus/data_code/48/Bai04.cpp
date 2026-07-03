#include <iostream>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;

    int sum1 = 0;
    for (int i = 1; i < a; i++) {
        if (a%i == 0) {
            sum1 +=i;
        }
    }

    int sum2 = 0;
    for (int i = 1; i < b; i++) {
        if (b%i == 0) {
            sum2 +=i;
        }
    }

    if (sum1 == b && sum2 == a) {
        cout << "1";
    }
    else {
        cout << "0";
    }

    return 0;
}
