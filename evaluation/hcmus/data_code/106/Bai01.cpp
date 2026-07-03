#include <iostream>
#include <cstring>
using namespace std;

void getData(int a[][100], int n)
{
	for (int i = 0; i < n; i++)
	{
		for (int j = 0; j < n; j++) cin >> a[i][j];
	}
}

bool check_doixungmaindiagonal(int a[][100], int n)
{
	for (int i = 0; i < n; i++)
	{
		for (int j = 0; j < n; j++)
		{
			if (a[i][j] != a[j][i])
			{
				cout << a[i][j] << " : " << a[j][i];
				return false;
			}
		}
	}
	return true;
}

bool check_doixungopdiagonal(int a[][100], int n)
{
	for (int i = 0; i < n-1; i++)
	{
		for (int j = 0; j < n - 1 - i; j++)
		{
			int space;
			space = (n - 1) - i - j;
			if (a[i][j] != a[i + space][j + space])
			{
				cout << a[i][j] << " : " << a[i + space][j + space];
				return false;
			}
		}
	}
}

bool check_doixung2arr(int a[][100], int n)
{
	if (check_doixungmaindiagonal(a, n) || check_doixungopdiagonal(a, n)) return true;
	else return false;
}



int main()
{
	int a[100][100], s_n, n;
	cin >> s_n;
	n = sqrt(s_n);
	getData(a, n);
	if (check_doixung2arr(a, n)) cout << "true";
	else cout << "false";
	return 0;
}