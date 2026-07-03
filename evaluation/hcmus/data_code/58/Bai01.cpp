#include <iostream>
using namespace std;

long long cal_sum(long long a, long long b)
{
	long long sum(0);
	for (int i = a; i <= b; i++)
	{
		if (i % 2 == 0) sum += (long long)i;
	}
	return sum;
}

int main()
{
	long long a, b, sum;
	cin >> a >> b;
	sum = cal_sum(a, b);
	cout << sum;
	return 0;
}