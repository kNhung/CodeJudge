#include <iostream>
#include <cmath>

using namespace std;

int main() {
	int n;
	do {
		cin>>n;
	} while(n <= 0);
	int binhPhuongN = n * n;
	int m = n, count = 0;
	while(m != 0) {
		count++;
		m = m / 10;
	}
	int power = pow(10, count);
	int temp = binhPhuongN % power;
	if(temp == n) {
		cout<<1;
	}
	else {
		cout<<0;
	}
	
	return 0;
}
