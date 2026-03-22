#include <iostream>
using namespace std;

int main(){
	int n, b, d, S;
	cout << "Nhap n: ";
	cin >> n;
	S = n * n;
	b = S - n;
	d = b / 10;
	if (b % 10 == 0){
			cout << "1";
	}
	if (b % 10 != 0){
		cout << "0";
	}
	return 0;
}
