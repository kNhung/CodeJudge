#include <iostream>
#include <cstring>

using namespace std;

const int MAX = 1000;

void deleteCharacter(char a[], int &n) {
	for (int i = 0; i < n - 1; i++) {
		if (a[i] == a[i + 1]) {
			for (int j = i; j <= n - 2; j++) {
				a[j] = a[j + 2];
			}
			
			n = n - 2;
			i = -1;
		}
	}
}

bool checkValid(char a[], int n) {
	for (int i = 0; i < n; i++) {
		if (a[i] < 97 || a[i] > 122) {
			cout << "Hay nhap lai!" << endl;
			return false;
		}
	}
	
	return true;
}

int main () {
	char c[MAX];
	int n = 0;
	
	do {
		cin.getline(c, MAX);
		n = strlen(c);
	} while (!checkValid(c, n));
	
	deleteCharacter(c, n);
	for (int i = 0; i < n; i++) {
		cout << c[i];
	}
	
	return 0;
}
