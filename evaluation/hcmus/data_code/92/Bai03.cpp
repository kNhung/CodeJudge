#include <iostream>

using namespace std;

bool checkReverse(int n)
{
	if (n == 0)
		return 0;
		
	int result = 0;
	int temp = n;
	
	while ( temp != 0){
		int ram = temp % 10;
		result = result * 10 + ram;
		temp /= 10;
	}
	
	if ( n == result)
		return 1;
	else
		return 0;
	
}

int delDigit(int n , int check)
{
	int result = -1;
	
	int left = n , right = 0 , pow = 1;
	while ( left != 0 ){
		int temp1 = left % 10;
		left /= 10;
			
		int temp2 = left*pow + right;
		
		///// check dung de danh dau so luong chu so can xoa
		if (check != 0)
			temp2 = delDigit(temp2 , check - 1);
	
		if ( checkReverse(temp2) && temp2 > result )
			result = temp2;
		
		right += temp1*pow;	
		pow *= 10;
	}
	
	return result;
}

int findMaxReverse(int n)
{
	int result;
	for (int i = 0 ; i < 2; i++ )
	{
		result = delDigit(n , i);
		if (result != -1)
			break;
	}
	return result;
}

int main()
{
	int n;
	cin >> n;

	cout << findMaxReverse(n);
	
	return 0;
}
