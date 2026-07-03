#include<iostream>
using namespace std;

long long cal_sumofdiv(long long n)
{
	long long res(1);
	for (long long i = 2; i < n; i++)
	{
		if (n % i == 0) res += i;
	}
	return res;
}

bool check_sobanbe(long long a, long long b)
{
	int temp1, temp2;
	temp1 = cal_sumofdiv(a); //temp1 la tong cac uoc khac a cua a
	temp2 = cal_sumofdiv(b); //temp2 la tong cac uoc khac b cua b
	if (temp1 == b || temp2 == a) return true;
	else return false;
}

int main()
{
	long long a, b;
	cin >> a >> b;
	if (check_sobanbe(a, b)) cout << 1;
	else cout << 0;
	return 0;
}