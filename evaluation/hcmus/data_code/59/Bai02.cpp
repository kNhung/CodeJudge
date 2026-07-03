//23127077

#include <iostream>

using namespace std;

int isAutomorphic(int n)
{
	if ((n % 10) == ((n * n) % 10)) 
	{
		return 1;
	}
	else
	{
		return 0;
	}

}

int main()
{
	int n;
	
	cout << "Nhap n: ";
	cin >> n;

	if (n > 0)
	{
		cout << isAutomorphic(n);
	}
	else
	{
		cout << "Wrong input";
	}
	
	return 1;
}
