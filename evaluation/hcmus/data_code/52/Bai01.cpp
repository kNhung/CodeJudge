// Đề bài: Viết chương trình tính tổng các số chẵn trong khoảng từ a đến b, trong đó a và b là hai số nguyên được nhập từ bàn phím (a <= b).


#include<iostream>
#include<cmath>
using namespace std;

bool SoChan(int n){
	if (n % 2 == 0)
		return true;
	return false;
}

int TongCacSoChan(int a, int b){
	int tong = 0;
	for (int i = a; i <= b; i++)
		if (SoChan(i))
			tong += i;
	return tong;
}

int main(){
    int a, b;
	cin >> a >> b;
	cout << TongCacSoChan(a, b) << endl;
	return 0;
}
