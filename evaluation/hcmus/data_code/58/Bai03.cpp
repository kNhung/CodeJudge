#include <iostream>
using namespace std;

int cal_sodocnguoc(int n)
{
	int res(0);
	while (n > 0)
	{
		int  temp1;
		temp1 = n % 10;
		res = (10 * res) + temp1;
		n /= 10;
	}
	return res;
}

bool check_sodoixung(int n)
{
	int sodocnguoc;
	sodocnguoc = cal_sodocnguoc(n);
	if (n < 10 ) return false;
	if (n == sodocnguoc) return true;
	else return false;
}

int find_sodoixungmax(int n)
{
	int max(-1), count(1);
	if (check_sodoixung(n)) return n;
	while (n >= count)
	{
		int temp1,temp2,temp3; //temp3 de luu gia tri sau khi xoa mot chu so
		temp1 = n % count;
		temp2 = n / (count * 10);
		temp3 = temp2 * count + temp1;
		if (check_sodoixung(temp3))
		{
			if (temp3 > max) max = temp3;
		}
		count *= 10;
	}
	return max;
}

int main()
{
	int n, max;
	cin >> n;
	max = find_sodoixungmax(n);
	cout << max;
	return 0;
}