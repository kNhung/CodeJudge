//23127077
#include <iostream>
#include <cstring>
#include <cmath>

using namespace std;

const int MAX = 100;

void nhapMang(int a[][MAX], int &n);
bool kiemtraDoiXung(int a[][MAX], int n);


int main()
{
	int a[100][100], n;
	nhapMang(a, n);
	cout << kiemtraDoiXung(a, n);
	
	return 0;
}

void nhapMang(int a[][MAX], int &n)
{
	cin >> n;
	
	if (n <= 0)
	{
		cout << "Wrong input!";
		return;
	}
	
	for (int i = 0; i < sqrt(n); i++)
	{
		for (int j = 0; j < sqrt(n); j++)
		{
			cin >> a[i][j];
		}
	}
}

bool kiemtraDoiXung(int a[][MAX], int n)
{
	int tmp = 0, tmp2 = 0;
	int n2 = sqrt(n) - 1;
	for (int i = 0; i <= n2 ; i++)
	{
		for (int j = 0; j <= n2; j++)
		{
			if (a[i][j] != a[n2 - j][n2 - i]) 
			{
				tmp++;
				break;
			}
		}
	}
	for (int i = 0; i <= n2; i++)
	{
		for (int j = n2; j > 0; j--)
		{
			if (a[i][j] != a[n2 - j][n2 - i]) 
			{
				tmp2++;
				break;
			}
		}
	}
	
	if (tmp == 0 || tmp2 == 0) return true;
	else return false;
}
