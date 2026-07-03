#include <iostream>
#include <cmath>

using namespace std;

int main()
{
	int a, b, sum = 0;
	cout << "Nhap so nguyen a, b: ";
	cin >> a >> b;
	for (int i = a; i <= b; i++)
	{
		if (i % 2 == 0)
			sum += i;
	}
	cout << "Tong cac so chan trong khoang [" << a << "," << b << "] la: " << sum;
	return 0;
}