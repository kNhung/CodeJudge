#include <iostream>

using namespace std;

int timSUoc(int n);
void soSanh(int a, int b);

int main() {
	int a, b;

	cin >> a;
	cin >> b;

	soSanh(a, b);

	return 0;
}

int timSUoc(int n) {
	int sum = 0;

	for (int i = 1; i < n; ++i) {
		if (n % i == 0)
			sum += i;
	}
	
	return sum;
}

void soSanh(int a, int b) {
	if ((timSUoc(a) == b) && (timSUoc(b) == a))
		cout << " 1 ";
	else
		cout << " 0 ";
}