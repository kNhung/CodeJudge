#include <iostream>

using namespace std;

int main() {
	int a, b;
	cin>>a;
	do {
		cin>>b;
	} while(a > b);
	int sum = 0;
	for(int i = a; i <= b; i++) {
		if(i % 2 == 0 && i >= 0) {
			sum = sum + i;
		}
	}
	cout<<sum;
	
	return 0;
}
