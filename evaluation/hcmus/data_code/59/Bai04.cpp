//23127077

#include <iostream>

using namespace std;

int SoBanBe(int a, int b)
{
	int TongUocA = 0, TongUocB = 0;
	
	for (int i = 1; i < a; i ++)
	{
		if (a % i == 0)
		{
			TongUocA += i;
		}
	}
	for (int i = 1; i < b; i ++)
	{
		if (b % i == 0)
		{
			TongUocB += i;
		}
	}
	
	return ((TongUocA == b && TongUocB == a) * 1);
}

int main()
{
	int a, b;
	
	cout << "Nhap a: ";
	cin >> a;
	cout << "Nhap b: ";
	cin >> b;
	
	if (a > 0 && b > 0)
	{
		cout << SoBanBe(a, b);
	}
	else
	{
		cout << "Wrong input";
	}
	
	return 1;
}
