#include <iostream>
using namespace std;

bool ktraSoDoiXung(int n) {
    int reverseNum = 0;
    while (n != 0) {
        int temp = n % 10;
        reverseNum = reverseNum * 10 + temp;
        n /= 10;
    }
    if (reverseNum > 99) {
        return true;
    } else {
        return false;
    }
}


int xoaSo(int n) {
    for (int i = 0; i < n; i++) {
    }
    //xoa so bat ky
    //ktra số đối xứng và so sánh
}

int main() {
    int n;
    cin >> n;

    int SoCanTim = xoaSo(n);
    cout << SoCanTim;

    return 0;
}