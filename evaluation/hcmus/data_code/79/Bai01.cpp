#include <iostream>

using namespace std;

int TinhTong (int x, int y)
{
	int Sum;
	Sum = 0;
	for (int i = x; i <= y; i++)
	{
		if (i % 2 == 0)
		{
			Sum = Sum + i;
		}
	}
	return Sum;
}
int main ()
{
	int a, b;
	cin >> a >> b;
	cout << TinhTong(a, b);
}
