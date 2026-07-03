#include <iostream>

using namespace std;

int sumDivision(int n)
{
	if ( n == 1 )
		return 0;
	
	int temp = 1;
	int i = 2;
	
	for ( ; i*i <= n ; i ++)
		if (n % i == 0)
			temp += i + (n / i);
			
	//neu n la so chinh phuong, thi tren vong lap ngay tai i-1 thi  (i-1)*(i-1) = n
	if ( (i-1) * (i-1) == n )
		temp -= (i-1);
		
	return temp;
}

bool checkFriendNum( int a , int b)
{
	int sum_div_a = sumDivision(a);
	int sum_div_b = sumDivision(b);
	
	if (sum_div_a == b && sum_div_b == a)
		return 1;
	else
		return 0;
}

int main()
{
	int a , b;
	cin >> a >> b;
	
	if ( checkFriendNum(a, b) )
		cout << 1;
	else
		cout << 0;
	
	return 0;
}
