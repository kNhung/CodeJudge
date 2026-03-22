#include <iostream>
#include <cmath> 

using namespace std;

int main()
{
	int n, dem(0), a;
	int b;
	
	do
	{
		cin >> n;
	
	}
	while (n <= 0);
	
	b = pow(n, 2);
	a = pow(n, 2);
	
	while (a != 0)
	{
		a = a / 10;
		dem++;
	}
	for (int i = 1; i <= dem; i++)
	{
		b = b % (pow(10, (dem - i)));
		if (b == n)
		{
			cout << 1;
			return 0;
		}
		
	}
	cout << 0;
	return 0;
}
