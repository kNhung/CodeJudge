#include <iostream>

using namespace std;

void checkAutomorphic(int n);
int checkCount(int n);

int main() {
	int n;

	cin >> n;

	if (n < 0)
		cout << " Wrong ";
	else
		checkAutomorphic(n);

	return 0;
}

int checkCount(int n) {
	int count = -1;

	while ((n * n) > 0) {
		++count;
		n /= 10;
	}

	return count;
}

void checkAutomorphic(int n) {
	int soBinhPhuong, count;

	soBinhPhuong = n * n;
	count = pow(10, checkCount(soBinhPhuong));

	if ((soBinhPhuong % count) == n)
		cout << " 1 ";
	else
		cout << " 0 ";
}