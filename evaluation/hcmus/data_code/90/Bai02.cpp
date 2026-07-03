#include <iostream>
#include <cmath>

using namespace std;

int demchuso(int n) {
	int count = 0;
	
	while (n > 0) {
		n /= 10;
		count++;
	}
	return count;
}

bool ktrso(int n) {
	int k = pow(n, 2);
	int sum = 0;
	
	for (int i = 1; i <= demchuso(k); i++) {
		sum += pow(10, i - 1) * (k % 10);
		k /= 10;
		if (sum == n) {
			return true;
		}
	}
	
	
}

int main() {
	int n;
	cin >> n;
	if (n > 0) {
		cout << ktrso(n);
	}
	else {
		cout << "Khong hop le";
	}
	
	return 0;
}