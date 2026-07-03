#include <iostream>
using namespace std;

int main() {
    int a, b;
    cout << "Input a = ";
    cin >> a;
    cout << "Input b = ";
    cin >> b;

    int sum = 0;
    for (int i = a; i <= b; i++) {
        if (i % 2 == 0) {
            sum += i;
        }
    }

    cout << sum << endl;

    return 0;
}