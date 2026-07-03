#include <iostream>

using namespace std;

int main() {
	int n;
	int soDao = 0;

	cin >> n;

	if (n < 1000 || n > 9999)
		cout << " Wrong ";
	else {
		int a, b, c, d;
		int truongHop;

		a = (n / 1) % 10;
		b = (n / 10) % 10;
		c = (n / 100) % 10;
		d = n % 1000;

		if (a == b)
			truongHop = 1;
		else if (a == c)
			truongHop = 2;
		else if (a == d)
			truongHop = 3;
		else if (b == c)
			truongHop = 4;
		else if (b == d)
			truongHop = 5;
		else if (c == d)
			truongHop = 6;
		else
			truongHop = 0;

		switch (truongHop) {
		case 1: {
			soDao = b * 10 + a;
		}
		case 2:
		{
			soDao = c * 100 + b * 10 + a;
		}
		case 3:
		{
			if (b >= c)
				soDao = d * 100 + b * 10 + a;
			else
				soDao = d * 100 + c * 10 + a;
		}
		case 4:
		{
			soDao = c * 10 + b;
		}
		case 5:
		{
			soDao = d * 100 + c * 10 + b;
		}
		case 6:
		{
			soDao = d * 10 + c;
		}
		case 0:
		{
			soDao = -1;
		}
		}
	}

	cout << soDao;

	return 0;
}