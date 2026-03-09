#include <iostream>

using namespace std;

bool ktrsodoixung(int n) {
	int k = 0;
	
	while (n > 0) {
		k = k * 10 + n % 10;
		n /= 10;
		if (k == n) {
		return true;
		}
	}
	
}

int main() {
	int n;
	cin >> n;
	cout << ktrsodoixung(n);
	
	return 0;
}