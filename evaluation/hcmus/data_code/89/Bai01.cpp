#include <iostream>
using namespace std;

bool checkEven (int n) {
    if (n % 2 == 0) {
        return true;
    } else {
        return false;
    }
}

int Sum (int a, int b) {
    int sum = 0;
    for (int i = a + 1; i < b; i++) {
        if (checkEven(i) == true) {
            sum += i;  
        }
    }
    return sum;
} 

int main() {
    int a, b;
    cin >> a >> b;
    
    int sum = Sum(a, b);
    cout << sum << endl;

    return 0;
}