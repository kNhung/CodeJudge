#include <iostream>

using namespace std;

int sumAllCommon(int n)
{
	int sum = 0;
	for (int i = 1; i < n; i++)
	{
		if (n % i == 0)
		{
			sum+= i;
		}
	}
	return sum;
}
int main()
{
	int a, b;
	cout << "Nhap a, b: ";
	cin >> a >> b;
	int sum1 = sumAllCommon(a);
	int sum2 = sumAllCommon(b);
	if (sum1 == b && sum2 == a)
		cout << 1;
	else
		cout << 0;
	return 0;
}
