#include<cmath>
#include <iostream>
using namespace std;

bool Check_auto(int a)
{
	int dem = 1;
	int a1 = a;
	while (a1 != 0)
	{
		a1 = a1 / 10;
		dem = dem * 10;
	}

	int temp = a * a;
	if (temp % dem == a)
	{
		return true;
	}
	return false;
}
int main()
{
	int a;
	cin >> a;
	cout << Check_auto(a);
	return 0;
}