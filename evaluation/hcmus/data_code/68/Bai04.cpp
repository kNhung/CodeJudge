#include <iostream> 

using namespace std;

int tinh_tong_cac_uoc(int n)
{
	int sum = 0;
	for (int i = 1; i < n; i++)
	{
		if (n % i == 0)
			sum = sum + i;
	}
	return sum;
}

bool ktra_banbe(int a, int b)
{
	int x = tinh_tong_cac_uoc(a);
	int y = tinh_tong_cac_uoc(b);
	
	if(x == b && y == a) return true;
	else return false;
}

int main ()
{
	int a, b;
	cout << "nhap a, b: ";
	cin >> a >> b;
	
	while (a <= 0)
	{
		cout << "nhap sai, nhap lai a: ";
		cin >> a;
	}
	
	while (b <= 0)
	{
		cout << "nhap sai, nhap lai b: ";
		cin >> b;
	}
	
	if(ktra_banbe(a, b)) cout << 1;
	else cout << 0;
	
	return 0;
}
