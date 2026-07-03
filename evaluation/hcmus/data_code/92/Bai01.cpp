#include <iostream>

using namespace std;

long long int sumEven( int left , int right)
{
	int temp = 0;
	for (int i = left ; i <= right; i ++)
		if (i % 2 == 0)
			temp += i;
	return temp;
}

int main()
{
	int a, b;
	cin >> a;
	cin >> b;
	
	cout << sumEven(a , b);
	
	return 0;
}
