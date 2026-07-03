#include <iostream>
#include <cmath>
using namespace std;

int cal_dig(int n)
{
	int count(0);
	while (n > 0)
	{
		n /= 10;
		count++;
	}
	return count;
}

bool check_automorphic(int n, int count, long long square_n)
{
	int temp1, temp2;
	temp1 = (int)pow(10, count);
	temp2 = square_n % temp1;
	if (temp2 == n) return true;
	else return false;
}

int main()
{
	int n,count;
	cin >> n;
	long long square_n;
	square_n = (long long)n * n;
	count = cal_dig(n);
	if (check_automorphic(n, count, square_n)) cout << 1;
	else cout << 0;
	return 0;
}