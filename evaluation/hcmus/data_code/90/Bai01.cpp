#include <iostream> 

using namespace std;

bool ktrsochan(int n) {
	if (n % 2 == 0) {
		return true;
	}
	else {
		return false;
	}		
	
}

int main() {
	int a, b;
	cout << "Nhap a: ";
	cin >> a;
	cout << "Nhap b: ";
	cin >> b;
	int sum = 0;
if (a <= b) {
	for (int i = a; i <= b; i++) {
		if (ktrsochan(i)) {
			sum += i;
		}
	}
}
cout << sum;

return 0;	
}