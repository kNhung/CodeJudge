#include <iostream>
#include <cstring>

using namespace std;

const int MAX = 1000;

struct DoiThi{
	int id;
	char name[40];
	int like;
	int comment;
	int share;
	int tong_diem;
};

struct BangDiem{
	int id;
	int tong_diem;
};

void nhapDoiThi(DoiThi &a, int id) {
	a.id = id;
	cout << "Name: ";
	cin.getline(a.name, MAX);
	cout << "Like: ";
	cin >> a.like;
	cout << "Commnent: ";
	cin >> a.comment;
	cout << "Share: ";
	cin >> a.share;
}

void xuatDoiThi(DoiThi a) {
	cout << "Name: " << a.name << endl;
	cout << "Like: " << a.like << endl;
	cout << "Comment: " << a.comment << endl;
	cout << "Share: " << a.share << endl;
	cout << endl;
}

void tinhDiemDoiThi(DoiThi &a) {
	a.tong_diem = a.like + a.comment*2 + a.share*3;
}

void nhapDanhSach(DoiThi a[], int &n) {
	n = 0;
	do {
		nhapDoiThi(a[n], n);
		n = n + 1;
		cin.ignore();
	} while(strcmp(a[n - 1].name, "000") != 0);
}

void tinhDiemCacDoiThi(DoiThi a[], int n) {
	for(int i = 0; i < n; i++) {
		tinhDiemDoiThi(a[i]);
	}
}

void luuTruBangDiem(DoiThi a[], int n, BangDiem b[]) {
	for(int i = 0; i < n; i++) {
		b[i].id = a[i].id;
		b[i].tong_diem = a[i].tong_diem;
	}
}

void sapXepBangDiem(DoiThi a[], int n, BangDiem b[]) {
	for(int i = 0; i < n; i++) {
		for(int j = i + 1; j < n; j++) {
			if(b[i].tong_diem > b[i + 1].tong_diem) {
				BangDiem tam = b[i];
				b[i] = b[i + 1];
				b[i + 1] = tam;
			} 
		}
	}
}

void xuatDoiThiTheoId(DoiThi a[], int n, int id) {
	for(int i = 0; i < n; i++) {
		if(a[i].id == id) {
			cout << a[i].name << endl;
			break;
		}
	}
}

void xuatCacDoiCaoDiemNhat(DoiThi a[], int n ,int so_doi) {
	BangDiem b[MAX];
	luuTruBangDiem(a, n, b);
	sapXepBangDiem(a, n, b);
	for(int i = 0; i < so_doi; i++) {
		xuatDoiThiTheoId(a, n, b[i].id);
	}
}

int main() {
	DoiThi danh_sach[MAX];
	int n;
	int so_doi = 3;
	
	nhapDanhSach(danh_sach, n);
	xuatCacDoiCaoDiemNhat(danh_sach, n, so_doi);
	
	return 0;
}
