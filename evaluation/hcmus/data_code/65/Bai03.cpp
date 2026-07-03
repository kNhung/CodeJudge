#include <iostream>
#include <cmath>

using namespace std;

bool kiemTraSoDoiXung (int n) {
	int NewNumber = 0;
	int temp = n;
	
	while (temp != 0) {
		int SoDu = temp % 10;
		NewNumber = NewNumber * 10 + SoDu;
		temp = temp / 10;
	}
	
	if (NewNumber == n) {
		return true;
	} else {
		return false;
	}
}

int inSoDoiXungLonNhat(int n) {
	int MaxNumber = 0;
	if (kiemTraSoDoiXung(n)) {
		return n;
	} else {
		int temp1 = n;
		int mu = 10;
		while (temp1 != 0) {
			int SoDu = temp1 % mu;
			int right = SoDu % (mu / 10);
			int left = temp1 / mu;
			int NewNumber = left * (mu / 10) + right;
			
			if (kiemTraSoDoiXung(NewNumber) == true && NewNumber >= MaxNumber) {
				MaxNumber = NewNumber;
			}
			
			mu = mu * 10;
		}
		
		if (MaxNumber != 0) {
			return MaxNumber;
		} else {
			int temp2 = n;
			int digit1 = temp2 / 1000;
			int digit2 = (temp2 % 1000) / 100;
			int digit3 = (temp2 % 100) / 10;
			int digit4 = temp2 % 10;
			
			int num1 = digit1 * 10 + digit3;
			int num2 = digit2 * 10 + digit3;
			int num3 = digit2 * 10 + digit4;
			
			mu = 100;
			while (temp2 != 0) {
				int SoDu = temp2 % mu;
				int right = SoDu % (mu / 100);
				int left = temp2 / mu;
				int NewNumber = left * (mu / 100) + right;
				
				if (kiemTraSoDoiXung (NewNumber) && NewNumber >= MaxNumber) {
					MaxNumber = NewNumber;
				}
				
				mu = mu * 10;	
			}
			
			int NewNumber = num1;
			if (kiemTraSoDoiXung (NewNumber) && NewNumber >= MaxNumber) {
				MaxNumber = NewNumber;
			}
			
			NewNumber = num2;
			if (kiemTraSoDoiXung (NewNumber) && NewNumber >= MaxNumber) {
				MaxNumber = NewNumber;
			}
			
			NewNumber = num3;
			if (kiemTraSoDoiXung (NewNumber) && NewNumber >= MaxNumber) {
				MaxNumber = NewNumber;
			}
			
			if (MaxNumber != 0) {
				return MaxNumber;
			} else {
				return -1;
			}
		}
	}
}

int main () {
	int n;
	
	cin >> n;
	
	if (n < 1000 || n > 9999) {
		cout << "DK cua n: 1000 <= n <= 9999";
	} else {
		cout << inSoDoiXungLonNhat(n);
	}
	
	return 0;
}
