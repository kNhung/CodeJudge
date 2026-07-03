#include<iostream>
using namespace std;

void nhapMang(int a[100][100], int &dong, int &cot) {
	cout << "Nhap dong: ";
	cin >> dong;
	cout << "Nhap cot: ";
	cin >> cot;
	for(int i=0; i<dong; i++) {
		for(int j=0; j<cot; j++) {
			cout << "Mang[" << i << "]: ";
			cin >> a[i][j];
		}
	}
}


void xuatMang(int a[100][100], int dong, int cot) {
	for(int i=0; i<dong; i++) {
		for(int j=0; j<cot; j++) {
			cout << a[i][j] << " ";
		}
		cout << "\n";
	}
}

void Hoanvi(int &a, int &b) {
	int c;
	c=a;
	a=b;
	b=c;
}


void doiMangDX(int a[100][100], int dong, int cot) {
	for(int i=0; i<dong; i++) {
		for(int j=0; j<cot/2; j++) {
			Hoanvi(a[i][j] , a[i][cot-j-1]);
		}
	}
}

int main() {
	int a[100][100], cot, dong;
    nhapMang(a, dong, cot);
	xuatMang(a, dong, cot);
	doiMangDX(a, dong, cot);
	xuatMang(a, dong, cot);
	return 0;
}



