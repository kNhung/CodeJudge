#include <iostream>

using namespace std;

bool ktrSoDoiXung(int n) {
	if(n <= 10) return false;
	else {
		int m = n, sdn = 0;
		while(m != 0) {
			sdn = sdn * 10 + m % 10;
			m = m / 10;
		}
		if(sdn == n) return true;
	}
	return false;
}

int timSoDoiXung(int n) {
	if(ktrSoDoiXung(n)) return n;
	else {
		int i = 10, dau, cuoi, temp, result = -1;
		while(i / 10 <= n) {
			dau = n / i;
			cuoi = n % i;
			cuoi = cuoi % (i / 10);
			temp = dau * (i / 10) + cuoi;
			if(result < temp && ktrSoDoiXung(temp))
				result = temp;
			int j = 10;
			while(j <= temp) {
				dau = temp / j;
				cuoi = temp % j;
				cuoi = cuoi % (j / 10);
				temp = dau * (j / 10) + cuoi;
				if(result < temp && ktrSoDoiXung(temp))
					result = temp;
				j = j * 10;
			}
			i = i * 10;
		}
		return result;
	}
}

int main() {
	int n;
	do {
		cin>>n;
	} while(n < 1000 || n > 9999);
	
	cout<<timSoDoiXung(n);
	
	return 0;
}
