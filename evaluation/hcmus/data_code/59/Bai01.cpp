//23127077

#include <iostream>

using namespace std;

void TongSoChan(int a, int b)
{
	if (b >= a)
	{
		int tong = 0;
		
		for (int i = a; i <= b; i++)
		{
			if (i % 2 == 0) 
			{
				tong += i;
			}
		}
		
		cout << tong;
	}
	else
	{
		cout << "Wrong input";
	}
}

int main()
{
	int a, b;
	
	cout << "Nhap a: ";
	cin >> a;
	cout << "Nhap b: ";
	cin >> b;
	
	TongSoChan(a, b);
	
	return 1;
}
