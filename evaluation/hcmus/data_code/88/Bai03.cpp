#include <iostream>
#include <cmath>
using namespace std;
int main() {
	int a, b, c, d=0, e, f, dem=1;
	cout << "Nhap vao mot so nguyen tu 1000 den 9999: ";
	cin >> a;
	if (a < 1000 || a >= 100000) cout << "Sai du lieu de bai";
	else {
		b = a % 100;//lấy hai số cuối
		c = a / 100;//lấy hai số đầu 
		while (b>0) {
			e = b % 10;
			d +=e* pow(10, dem);
			b = b / 10;
			dem--;
		}
		if (c == d) cout << a;
	} //so sánh số vd như 1221 1331 thì sẽ không cắt bỏ số nào hết
	return 0;
}