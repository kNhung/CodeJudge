#include <iostream>

using namespace std;

bool findOddNum(int n);
int findSum(int a, int b);

int main() {
	int a, b;
	int sum = 0;

	cin >> a;
	cin >> b;

	if (a > b) {
		cout << " Wrong ";
	} else {
		sum = findSum(a, b);
		cout << sum;
	}

	return 0;
}

bool findOddNum(int n) {
	if (n % 2 == 0)
		return true;
	else
		return false;
}

int findSum(int a, int b) {
	int sum = 0;

	for (int i = a; i <= b; ++i) {
		if (findOddNum(i))
			sum += i;
	}
	
	return sum;
}