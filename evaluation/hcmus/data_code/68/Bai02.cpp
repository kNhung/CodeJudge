#include <iostream> 
#include <cmath>

using namespace std;

int dem_chu_so(int n)
{
	int count = 0;
	while (n != 0)
	{
		n = n / 10;
		count++;
	}
	return count;
}

bool isAutomorphic (int n)
{
	int m = dem_chu_so(n);
	int x = pow(n, 2);
	int y = pow(10, m);
	
	int r = x % y;
	if (r == n) return true;
	else return false;
}

int main ()
{
	int n;
	cout << "nhap n: ";
	cin >> n;
	
	while (n <= 0)
	{
		cout << "hay nhap n la so tu nhien, nhap n: "; 
		cin >> n;
	}
	
	if(isAutomorphic(n)) cout << 1;
	else cout << 0;
	
	return 0;
}
