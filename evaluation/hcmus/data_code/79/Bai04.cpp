#include <iostream>
#include <cmath>

using namespace std;

int TongUoc (int x)
{
	int Tong;
	Tong = 1;
	for (int i = 2; i <= sqrt(x); i++)
	{
		if (x % i == 0)
		{
			Tong = Tong + i;
			Tong = Tong + (x / i);
		}
	}
	return Tong;
}

int main ()
{
	int a, b;
	cin >> a >> b;
	if ((TongUoc(a) == b) && (TongUoc(b) == a)) 
	{
		cout << 1;
	}
	else 
	{
		cout << 0;
	}
	return 0;
}
