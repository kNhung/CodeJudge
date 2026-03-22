#include <iostream>
#incluse <cmath>;
using namespace std;

void inMaxDX(int n) {
	int count;
	float x= float(n);
	while (x/10 >= 1) 
		count ++;
		
	while (count != 0) {
		count --;
		int DonVi = x%10;
		x/10;
		while (count != 0)
			count --;
	}
	
}

int main () {
	int n;
	cin >> n;
	
	inMaxDX (n);
}

