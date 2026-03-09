#include <iostream>

using namespace std;

int tinh_tong_so_chan(int a, int b)
{
	int sum = 0;
	for (int i = a; i <= b; i++)
	{
		if (i % 2 == 0)
			sum = sum + i;
	}
	return sum;
}

int main()
{
	int a, b; 
	cout << "nhap a, b: ";
	cin >> a >> b;
	
	if (a > b) cout << "nhap loi" << endl; 
	
	int sum = tinh_tong_so_chan(a,b);
	cout << "output: " << sum;
}
