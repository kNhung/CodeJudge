#include <iostream>

using namespace std;

int isFriend(int a, int b) {
    int sumGDCa(0);
    int sumGDCb(0);

    for (int i = 1; i < a; i++) {
        if ((a % i) == 0) {
            sumGDCa += i;
        }
    }

    for (int j = 1; j < b; j++) {
        if ((b % j) == 0) {
            sumGDCb += j;
        }
    }
    if ((sumGDCa == b) && (sumGDCb == a)) {
        return 1;
    }
    return 0;
}

int main() {
    int a, b;
    cin >> a >> b;

    cout << isFriend(a, b);
    return 0;
}