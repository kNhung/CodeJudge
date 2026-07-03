#include <iostream>
using namespace std;

void ktraBanBe (int a, int b) {
	int SumA(0), SumB(0);
	
	for (int i = 1; i <= a/2; i++) {
		if (a % i == 0)
			SumA += i;	
	}
	for (int i = 1; i <= b/2; i++) {
		if (b % i == 0)
			SumB += i;	
	}

	if (a <= 0 || b <= 0)
		cout << "Nhap lai";
	else {
		if ( SumA =  b && SumB == a)
			cout << "1";
		else
			cout << "0";
	}
	
}

int main () {
	int a, b;
	cin >> a >> b;
	ktraBanBe(a,b);
		
	
	return 0;
}

