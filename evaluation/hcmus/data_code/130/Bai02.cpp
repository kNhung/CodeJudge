#include <iostream>
#include <cstring>

using namespace std;

const int MAX = 1000;

int ktraChuoiCoPhanTuNoiTiep(char str[]) {
	int len = strlen(str);
	for(int i = 0; i < len - 1; i++) {
		if(str[i] == str[i + 1]) return 1;
	}
	return 0;
}

void xoaChuoiCon(char str[], int dau, int cuoi) {
	int do_dai = cuoi + 1 - dau;
	int len = strlen(str);
	for(int k = 0; k < do_dai; k++) {
		for(int i = dau; i < len; i++) {
			str[i] = str[i + 1];
		}
		str[len - 1] = '\0';
	}
}

void xacDinhViTri(char str[], int &dau, int & cuoi) {
	int len = strlen(str);
	for(int i = 0; i < len - 1; i++) {
		if(str[i] == str[i + 1]) {
			dau = i;
			break;
		}
	}
	for(int i = dau; i < len; i++) {
		if(str[i] != str[i + 1]) {
			cuoi = i;
			break;
		}
	}
}

void xoaChuoiKyTuTrungNhau(char str[]) {
	int dau;
	int cuoi;
	while(ktraChuoiCoPhanTuNoiTiep(str)) {
		xacDinhViTri(str, dau, cuoi);
		xoaChuoiCon(str, dau, cuoi);
	}
}

int main() {
	char str[MAX];
	
	cin.getline(str, MAX);
	xoaChuoiKyTuTrungNhau(str);
	cout << str;
	
	return 0;
}
