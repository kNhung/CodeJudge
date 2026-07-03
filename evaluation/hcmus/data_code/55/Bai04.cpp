#include<cmath>
#include <iostream>
using namespace std;

int Sum_uoc(int a) {
	int sum = 0;
	for (int i = 1; i < a; i++)
	{
		if (a % i == 0)
		{
			sum += i;
		}
	}
	return sum;
}
bool CheckFriend(int a, int b)
{
	if ((Sum_uoc(a) == b) && (Sum_uoc(b) == a))
		return true;
	return false;
}
int main()
{
	int a, b;
	cin >> a >> b;
	cout << CheckFriend(a, b);
	return 0;
}