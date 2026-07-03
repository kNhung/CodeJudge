#include <iostream>

using namespace std;

int KiemTraDoiXung (int x)
{
	int DoiXung, SoDoiXung;
	DoiXung = x;
	SoDoiXung = 0;
	if (x < 10)
	{
		return 0;
	}
	while (DoiXung > 0)
	{
		SoDoiXung = SoDoiXung * 10 + DoiXung % 10;
		DoiXung = DoiXung / 10;
	}
	if (SoDoiXung == x)
	{
		return 1;
	}
	return 0;
}
int XoaSo (int SoNguyen)
{
	int Max, j, BienLuuSo;
	Max = 0;
	j = 1;
	while (j <= SoNguyen)
	{
		BienLuuSo = (SoNguyen / (j * 10)) * j + (SoNguyen % j);
		if ((KiemTraDoiXung(BienLuuSo) == 1) && (Max < BienLuuSo))
		{
			Max = BienLuuSo;
		}
		j = j * 10;
	}
	return Max;
}
int main ()
{
	int n, SoLonNhat, BienPhu,k;
	cin >> n;
	if (KiemTraDoiXung(n) == 1)
	{
		cout << n;
		return 0;
	}
	else 
	{
		if (XoaSo(n) > 0)
		{
			cout << XoaSo(n);
			return 0;
		}
		else
		{
			k = 1;
			SoLonNhat = 0;
			while (k <= n)
			{
			BienPhu = (n / (k * 10)) * k + (n % k);
			if ((XoaSo(BienPhu) > 0) && (SoLonNhat < XoaSo(BienPhu)))
			{
				SoLonNhat = XoaSo(BienPhu);
			}
			k = k * 10;
			}
			if (SoLonNhat > 0)
			{
				cout << SoLonNhat;
				return 0;
			}
			else 
			{
				cout << -1;
				return 0;
			}
		}
	}
}
