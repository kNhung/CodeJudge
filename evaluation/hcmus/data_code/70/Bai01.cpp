#include <iostream>

using namespace std;

int solve(int a, int b) {
    int sum;
    if (b < a) {
        return 0;
    }

    for (int i = a; i <= b; i++) {
        if (i % 2 == 0) {
            sum += i;
        }
    }
    return sum;
}
int main() {
    int a, b;
    cin >> a >> b;

    cout << solve(a, b);
    return 0;
}