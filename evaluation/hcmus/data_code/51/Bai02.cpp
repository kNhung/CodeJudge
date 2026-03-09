#include <iostream>
#include <cmath>
using namespace std;

int countLength(int n) // Count numbers of digits in int n
{
	int count = 0;
	while (n > 0)
	{
		n /= 10;
		count++;
	}
	return count;
}

bool checkAutomorphic(int n)
{
	if (n <= 0)
		return false;
	return n * n % int(pow(10, countLength(n))) == n;
}

int main()
{
	int n;
	cout << "Please enter int n to check automorphic: ";
	cin >> n;
	cout << checkAutomorphic(n) << endl;
	return 0;
}