#include <iostream>
#include <cmath>

using namespace std;

int main() {
	int n, k;
	cin >> n;
	k = n * n;
	int dem = 0;
	int m = n;
	while (n > 0) {
		n = n / 10;
		dem++;
	}
	int h = k % int(pow(10, dem));
	if (h == m) {
		cout << 1;
	} else cout << 0;
	return 0;
}
