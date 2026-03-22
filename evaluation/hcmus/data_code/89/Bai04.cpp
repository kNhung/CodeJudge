#include <iostream>
using namespace std;

int TongUocSo (int n) {
    int sum = 0;
    for (int i = 1; i < n; i++) {
        if (n % i == 0) {
            sum += i;
        }
    }
    return sum;
}

int ktraSoBanBe(int a, int b) {
    if (TongUocSo(a) == b) {
        return 1;
    } else if (TongUocSo(b) == a) {
        return 1;
    } else {
        return 0;
    }
} 

int main() {
    int a, b;
    cin >> a >> b;

    int ktra = ktraSoBanBe(a, b);
    cout << ktra << endl;

    return 0;
}