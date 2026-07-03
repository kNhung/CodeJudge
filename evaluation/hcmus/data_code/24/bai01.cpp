#include<iostream>
using namespace std;


void nhapmang(int a[100], int &n) {
	cout << "Input number of disks: ";
	cin >> n;
	for(int i=0; i<n; i++) {
		a[i]=i+1;
	}
	cout << "\n";
}

void xuatdia(int a[100], int n) {
	cout << "Disk stack: ";
	for(int i=0; i<n; i++) {
		cout << a[i] << " ";
	}
	cout <<"\n";
}

void datlenDau(int a[100], int n, int  vitridoi ) {
	int tam=a[vitridoi];
	for(int i=vitridoi; i>0; i--) {
		a[i]=a[i-1];
	}
	a[0]=tam;
}

void doidia(int a[100], int b[100], int n, int solandoi) {
	for(int i=0; i<n; i++) {
		for(int j=0; j<solandoi; j++) {
			if(a[i]==b[j]) {
				datlenDau(a, n, i);
			}
		}
	}
}

int main() {
	int dia[100], diadoi[100], n;
	int landoi;
	nhapmang(dia, n);
	cout << "Input number of changes: " ;
	cin >> landoi;
	cout << "Dia doi: ";
	for(int i=0; i<landoi; i++) {
		cin >> diadoi[i];
	}
	doidia(dia, diadoi, n, landoi);
	xuatdia(dia, n);
	return 0;
}
