#include <iostream>
#include <cmath>

using namespace std;

bool isPalindrome(int num) {
    if (num < 10) return false;
    int rev = 0, original = num, remainder;
    while (num != 0) {
        remainder = num % 10;
        rev = rev * 10 + remainder;
        num /= 10;
    }
    return original == rev;
}

int remove(int number, int digitIndex) {
    int left = number / pow(10, digitIndex + 1);
    int right = number % static_cast<int>(pow(10, digitIndex));
    return left * pow(10, digitIndex) + right;
}

int findLargestPalindrome(int n) {
    int maxPalindrome = 0;
    int numDigits = floor(log10(n)) + 1;

    for (int i = 0; i < numDigits; i++) {
        int reducedNum = remove(n, i);
        if (isPalindrome(reducedNum)) {
            maxPalindrome = max(maxPalindrome, reducedNum);
        }
    }

    return maxPalindrome;
}

int main() {
    int n;
    cout << "Input: ";
    cin >> n;

    if (n < 1000 || n > 9999) {
        cout << "Error, input again. " << endl;
        return 1;
    }

    int largestPalindrome = findLargestPalindrome(n);
    cout << "Output: " << largestPalindrome << endl;

    return 0;
}
