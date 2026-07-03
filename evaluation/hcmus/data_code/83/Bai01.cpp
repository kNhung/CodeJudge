#include <iostream>
using namespace std;

int main(){
	int a, b, S;
	cout << "Nhap a: ";
	cin >> a;
	cout << "Nhap b: ";
	cin >> b;
	S = 0;
	if(b%2==0){
		for(int i = a; i <= b; ++i){
		if(a%2==0){
			S = S + a;
			}
		++a;
		}
		cout << S;
	}
	if(b%2!=0){
		for(int i = a; i < b; ++i){
		if(a%2==0){
			S = S + a;
			}
		++a;
		}
		cout << S;
	}
	return 0;
}
