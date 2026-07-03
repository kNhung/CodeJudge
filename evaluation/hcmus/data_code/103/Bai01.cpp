
#include <iostream>
#include<cstring>
#include<cmath>

#define MAX 100
using namespace std;



bool checkDoiXung(int a[MAX], int n) {
	for (int i = 0; i < n / 2; i++)
	{
		if (a[i] != a[n - 1 - i])
		{
			return false;
		}
	}
	return true;
}
bool check(int a[][MAX], int n) {
	bool check = true;
	int a_chinh[MAX] = { 0 };
	for (int i = 0; i < sqrt(n); i++) {
		a_chinh[i] = a[i][i];
	}

	int a_phu[MAX] = { 0 };
	for (int i = 0; i < sqrt(n); i++) {
		a_phu[i] = a[n - 1 - i][i];
	}

	if (checkDoiXung(a_chinh, sqrt(n)) || checkDoiXung(a_chinh, sqrt(n)))
	{
		return true;
	}
	else
		return false;
}
int main()
{
	int a[MAX][MAX];
	int n;
	cin >> n;
	for (int i = 0; i < sqrt(n); i++)
	{
		for (int j = 0; j < sqrt(n); j++)
		{
			cin >> a[i][j];
		}
	}

	cout << check(a, n);
}

