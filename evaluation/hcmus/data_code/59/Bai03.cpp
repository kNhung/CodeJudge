//23127077

#include <iostream>

using namespace std;

void SoDoiXung(int n)
{
	int 
	FirstDigit = n % 10,
	SecondDigit = (n / 10) % 10,
	ThirdDigit = (n / 100) % 10,
	ForthDigit = (n / 1000) % 10;
	
	if (FirstDigit == ForthDigit && ThirdDigit == SecondDigit)
	{
		cout << n << "(xoa 0 chu so)";	
	}	
	else if (FirstDigit == ForthDigit && ThirdDigit >= SecondDigit)
	{
		cout << ForthDigit * 100 + FirstDigit * 1 + ThirdDigit * 10 << "(xoa 1 chu so " << SecondDigit << " )";
	}
	else if (FirstDigit == ForthDigit )
	{
		cout << ForthDigit * 100 + FirstDigit * 1 + SecondDigit * 10 << "(xoa 1 chu so " << ThirdDigit << " )";
	}
	else if (FirstDigit == ThirdDigit && FirstDigit >= SecondDigit)
	{
		cout << ForthDigit * 100 + SecondDigit * 1 + ThirdDigit * 10 << "(xoa 1 chu so " << FirstDigit << " )";
	}
	else if (ForthDigit == SecondDigit)
	{
		cout << FirstDigit * 1 + SecondDigit * 10 + ThirdDigit * 100 << "(xoa 1 chu so " << ForthDigit << " )";
	}
	else if (FirstDigit == SecondDigit && FirstDigit >= ThirdDigit)
	{
		cout << FirstDigit * 1 + SecondDigit * 10  << "(xoa 2 chu so " << ForthDigit << ", " << ThirdDigit << " )";
	}
	else if (ForthDigit == ThirdDigit)
	{
		cout << ThirdDigit * 1 + ForthDigit * 10 << "(xoa 2 chu so " << FirstDigit << ", " << SecondDigit << " )";
	}
	else
	{
		cout << -1;
	}
	
	return;
}

int main()
{
	int n;
	
	cout << "Nhap n:";
	cin >> n;
	SoDoiXung(n);
	
	return 1;
}
