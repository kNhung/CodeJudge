#include <iostream>

using namespace std;

int tongUocSo(int n) {
	int tong = 0;
	for(int i = 1; i < n; i++) {
		if(n % i == 0) {
			tong = tong + i;
		}
	}
	return tong;
}

int ktraSoBanBe(int a, int b) {
	int tongUocSoA = tongUocSo(a);
	int tongUocSoB = tongUocSo(b);
	if(tongUocSoA == b || tongUocSoB == a)
		return 1;
	else
		return 0;
}

int main() {
	int a, b;
	do {
		cin>>a;
		cin>>b;
	} while(a <= 0 || b <= 0);
	
	cout<<ktraSoBanBe(a, b);
	
	return 0;
}
