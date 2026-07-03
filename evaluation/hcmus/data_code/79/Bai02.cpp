#include <iostream>
#include <cmath>

using namespace std;

bool KtraAuto(int x)
{
	int BinhPhuong;
	BinhPhuong = x * x;
	while (x > 0)
	{
		if ((x % 10) != (BinhPhuong % 10))
		{
			return 0;
		}
		x = x / 10;
		BinhPhuong = BinhPhuong / 10;
	}
	return 1;
}
int main ()
{
	int n;
	cin >> n;
	cout << KtraAuto(n);
	return 0;
}
