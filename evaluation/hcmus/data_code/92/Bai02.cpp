#include <iostream>

using namespace std;

bool checkAutomorphic(int n)
{
	long long int square_n = n*n;
	
	int pow = 1;
	while ( n / pow != 0){
		pow *= 10;
	}
	
	if (square_n % pow == n)
		return 1;
	else
		return 0;
}

int main()
{
	int n;
	cin >> n;
	
	cout << checkAutomorphic(n);
	
	return 0;
}
