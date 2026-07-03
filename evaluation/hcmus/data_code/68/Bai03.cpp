#include <iostream> 

using namespace std;

int viet_so_dao_nguoc(int n)
{
	int so_dao_nguoc = 0;
	while (n != 0)
	{
		int r = n % 10;
		so_dao_nguoc = so_dao_nguoc * 10 + r;
		n = n / 10;
	}
	return so_dao_nguoc;
}

bool ktra_so_doi_xung(int n)
{
	int m = viet_so_dao_nguoc(n);
	if (m == n) return true; 
	else return false;
}

int tim_so_doi_xung_lon_nhat(int n)
{
	int so_moi = 0;
	int pow = 1;
	int m = n;
	
	int max = -1;
	
	while (n != 0)
	{
		int r = m % pow;
		n = n / 10;
		so_moi = n * pow + r;
		
		if(ktra_so_doi_xung(so_moi)) 
		{
			if (so_moi >= max)
				max = so_moi;
		}
		
		pow = pow * 10;
	}
	
	return max;
}

int main ()
{
	int n;
	cout << "nhap n: ";
	cin >> n;
	
	while (n < 1000 || n > 9999)
	{
		cout << "hay nhap n thuoc [1000, 9999], nhap n: ";
		cin >> n;
	}
	
	int x = tim_so_doi_xung_lon_nhat(n);
	
	cout << x;
	
	return 0;
}
