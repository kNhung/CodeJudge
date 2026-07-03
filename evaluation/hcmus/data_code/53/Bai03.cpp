#include <iostream>

using namespace std;

int isPalindrome(int n)
{
	int reversed = 0, temp = n;
	while (temp > 0)
	{
		int q = temp % 10;
		reversed = reversed * 10 + q;
		temp /= 10;
	}
	if (reversed == n)
		return 1;
	return 0;
}
int largestPalindrome(int n) 
{
	int max = 0;
	for (int i = 1; i < 4; i++)
	{
		int temp = n;
		for (int i = 1; i < 4; i++)
		{
			temp = temp / (i * 10); //+ (i - 1) * 10;
			cout << temp << " ";
			if (isPalindrome(temp) && max < temp)
				max = temp;
		}
	}
	return max;
}
int main()
{
	int n;
	cout << "Nhap n: ";
	cin >> n;
	cout << largestPalindrome(n);
	return 0;
}

