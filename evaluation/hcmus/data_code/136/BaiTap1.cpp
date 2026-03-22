//23127450 Trương Vủ Phát

#include <iostream>

using namespace std;
   
const int Max = 1000;

//nhap mang vao
void Nhapmang(int a[][Max], int n) {
	for (int i = 0; i < n; i++) {
		for (int j = 0; j < n; j++) {
			cin >> a[i][j];
		}
	}
}

void duongcheochinh(int a[][Max], int n) {
	int b[Max];//tach cac phan tu trong mang 2 chieu ra va so sanh
	int c[Max];//tach cac phan tu trong mang 2 chieu ra va so sanh
	int k = 0, l = 0; // bien dem phan tu cua 2 mang 1 chieu sau khi tach ra
	for (int i = 1; i < n; i++) {
		for (int j = 0; j < i; j++) {
			b[k] = a[i][j];  // giong vd de bai thi cho nay se luu vao mang b[]={
			k++;
		}
	}
	for (int i = 0; i < n-1; i++) {
		for (int j = i+1; j < n; j++) {
			c[l] = a[i][j];
		}
	}
	while (k > 0) {
		if (c[k] != b[k]) { 
			cout << "false";
			break;
		}
		k--;
	}
	cout << "True";
}
//duong cheo phu
void duongcheophu(int a[][Max], int n) {
	int b[Max];//tach cac phan tu trong mang 2 chieu ra va so sanh
	int c[Max];//tach cac phan tu trong mang 2 chieu ra va so sanh
	int k = 0, l = 0; // bien dem phan tu cua 2 mang 1 chieu sau khi tach ra
	for (int i = 0; i < n - 1; i++) {
		for (int j = 0; j < n-i-1; j++) {
			b[k] = a[i][j]; // dua ra ve 1 mang 2 chieu roi ss phan tu
			k++;            //   123  
			                //   452     
		}					//   741  thi mang do se ra la 2-1-4
  	}                       
		for (int j = 1; j < n; j++) {
			for(int i=n-1;i>0;i-- ){
			c[l] = a[i][j];  // tuong tu
			n--;
		}
	}
	while (k > 0) {
		if (c[k] != b[k]) {
			cout << "false";
			break;
		}
		k--;
	}
	cout << "True";
}


int main() {
	int a[Max][Max];
	int n, dodai=0;
	cin >> n;
	if (n <= 0) {
		cout << "false";
		return 0;
	}
	else {
		for (int i = 2; i * i <= n;i++) {
			if (i * i == n) {
				dodai = i; // tinh do dai cua mang 
			}
		}
		if (dodai * dodai != n) cout << "false";
	}
	Nhapmang(a, dodai);
	duongcheochinh(a, dodai);
	duongcheophu(a, dodai);
	return 0;
}