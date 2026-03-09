#include <iostream>
#include <cmath>
#include <cstring>

using namespace std;

int CheckingDuongCheoChinh(int a[100][100], int n)
{
	for (int i = 0; i < n - 1; i++)
	{
		for (int j = 0; j <= n - 1; j++)
		{
			if (i != j)
			{
				if (a[i][j] != a[n - 1 - i][n - 1 - j])
				{
					return 0;
				}
			}
		}
	}
	return 1;
}

int CheckingDuongCheoChinh2(int a[100][100], int n)
{
	for (int i = 0; i < n - 1; i++)
	{
		for (int j = 0; j <= n - 1; j++)
		{
			if (i != j)
			{
				if (a[i][j] != a[j][i])
				{
					return 0;
				}
			}
		}
	}
	return 1;
}


int CheckingDuongCheoPhu(int a[100][100], int n)
{
	for (int i = 0; i <= n - 1; i++)
	{
		for (int j = 0; j <= n - 1; j++)
		{
			if ((i + j) != (n - 1))
			{
				if (a[i][j] != a[n - 1 - i][n - 1 - j])
				{
					return 0;
				}
			}
		}
	}
	return 1;
}

int CheckingDuongCheoPhu2(int a[100][100], int n)
{
	for (int i = 0; i <= n - 1; i++)
	{
		for (int j = 0; j <= n - 1; j++)
		{
			if ((i + j) != (n - 1))
			{
				if (a[i][j] != a[n - 1 - j][n - 1 - i])
				{
					return 0;
				}
			}
		}
	}
	return 1;
}

void output(int a[100][100], int n)
{
	if ((CheckingDuongCheoChinh(a,n) || CheckingDuongCheoPhu(a,n) || CheckingDuongCheoChinh2(a,n) || CheckingDuongCheoPhu2(a,n)) == 1) 
	{
		cout << "True";
	}
	else 
	{
		cout << "False";
	}
}

int main()
{
	int Mang[100][100];
	int SoPhanTu;
	int Size;
	std::cin >> SoPhanTu;
	Size = sqrt(SoPhanTu);
	for (int i = 0; i <= Size - 1; i++)
	{
		for (int j = 0; j <= Size - 1; j++)
		{
			std::cin >> Mang[i][j];
		}
	}
	output(Mang,Size);
	return 0;
}


