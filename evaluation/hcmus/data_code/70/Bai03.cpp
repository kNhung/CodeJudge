#include <iostream>

using namespace std;

int isDoixung(int n) {
    int reverse(0);
    int tmp = n;
    while (tmp != 0) {
        reverse = (reverse * 10) + (tmp % 10);
        tmp /= 10;
    }

    if (n == reverse) {
        return 1;
    }
    return 0;
}

int timSoDoixung(int n) {
    int max(0);

    if (isDoixung(n)) {
        return n;
    } else {
        int i = 10;
        while (i < n) {
            int tmp = (n / i) * (i / 10) + (n % (i / 10));
            if (isDoixung(tmp)) {
                if (tmp > max) {
                    max = tmp;
                } 
            } else if ((tmp % 100) != 0) {
                int j = 10;
                while (j < tmp) {
                    int tmp1 = (tmp / j) * (j / 10) + (tmp % (j / 10));
                    if (isDoixung(tmp1)) {
                        if (tmp1 > max) {
                            max = tmp1;
                        }
                    }
                    j *= 10;
                }
            }
            i *= 10;
        }
    }
    if (max == 0) {
        return -1;
    } else {
        return max;
    }

}

int main() {
    int n;
    cin >> n;

    cout << timSoDoixung(n);
    return 0;
}