#include <iostream>

using namespace std;

int main()
{
	int a, b, sum_a(0), sum_b(0);
	
	do
	{
		cin >> a;
		cin >> b;
	}
	while (a <= 0 && b <= 0);
	for (int i = 1; i < a; i++)
	{
		if (a % i == 0)
		    sum_a += i;
	}
	for (int i = 1; i < b; i++)
	{
		if (b % i == 0)
		    sum_b += i;
	}
	if (sum_a == b && sum_b == a)
	{
		cout << 1;
	}
	else 
	{
		cout << 0;
	}
	
	return 0;
}
