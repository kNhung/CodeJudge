#include <iostream>
using namespace std;

void inTongSoChan(int a, int b) {
	int Sum= 0;
	for (int x= a; x<= b; x++) {
		if (x % 2 == 0) 
			Sum += x;
	}
	cout << Sum;
}

int main () {
	int SoThuNhat, SoThuHai;
	cout << "Nhap a = ";
	cin >> SoThuNhat;
	cout << "Nhap b = ";
	cin >> SoThuHai;
	
	if (SoThuNhat > SoThuHai )
		cout << "Nhap lai";
	if (SoThuNhat <= SoThuHai )
		inTongSoChan(SoThuNhat, SoThuHai);
		
	return 0;
	
}
