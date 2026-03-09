	#include <iostream>
	#include <cmath>
	using namespace std;
	int main() {
		int a, b, c, d = 0, dem = 0;
		cout << "Hay nhap vao mot so automorphic: ";
		cin >> a;
		b = a * a;
		while (b > 0) {
			c = b % 10;
			b = b / 10;
			d += c * pow(10, dem);
			dem++;
			if (d == a) {
				cout << true;
				break;
			}
			else cout << false;
		}
		return 0;
	}