#include <iostream>
using namespace std;

int sumDevisors(int n)
{
	int sum = 0;
	for (int i = 1; i <= n/2; i++)
	{
		if (n % i == 0)
		{
			sum += i;
		}
	}
	return sum;
}

bool checkFriendNumber(int num1, int num2)
{
	if (num1 < 0 || num2 < 0) 
		return false;
	return (sumDevisors(num1) == num2) && (sumDevisors(num2) == num1);
}

int main()
{
	int num1, num2;
	cout << "Please enter int num1 to check friend number: ";
	cin >> num1;
	cout << "Please enter int num2 to check friend number: ";
	cin >> num2;
	cout << sumDevisors(num1) << endl << sumDevisors(num2) << endl;
	if (checkFriendNumber(num1, num2))
	{
		cout << num1 << " and " << num2 << " are friend numbers.\n";
	}
	else
	{
		cout << num1 << " and " << num2 << " are NOT friend numbers.\n";
	}
	return 0;
}