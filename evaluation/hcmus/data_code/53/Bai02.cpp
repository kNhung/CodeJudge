#include <iostream>
#include <cmath>

using namespace std;

int isAutomorphic(int n)
{
	int square = pow(n, 2);
	int countNum = 0;
	int temp = n;
	while (temp > 0)
	{
		countNum++;
		temp /= 10;
	}
	int divisor = pow(10, countNum);
	int q = square % divisor;
	if (n == q)
		return 1;
	else
		return 0;
}
int main()
{
	int n;
	cout << "Nhap n: ";
	cin >> n;
	cout << isAutomorphic(n);
	return 0;
}
