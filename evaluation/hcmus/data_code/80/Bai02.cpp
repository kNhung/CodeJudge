#include <iostream>
using namespace std;

void ktraAutomorphic(int a){
	int n = a;
	int BinhPhuong = n * n;
	int DonViSo = 0, DonViBP = 0;
	int TinhDung;
	while (n >= 1) {
		DonViBP = BinhPhuong % 10;
		DonViSo = n % 10;
		BinhPhuong /= 10;
		n= float(n) / 10;
		if (DonViSo == DonViBP)
			TinhDung = 1;
		else {
			TinhDung = 0;
			break;
		}
	}
	cout << TinhDung;
}

int main () {
	int So;
	cout << "Nhap So: ";
	cin >> So;
	
	ktraAutomorphic(So);
	
	return 0;
}

