#include <iostream>
using namespace std;

int main(void){
	int a[100], n, m, temp = 1, change, pos;
	cout << "Input number of disks: ";
	cin >> n;
	for (int i = 0; i < n; i++){
		a[i] = i + 1;
	}
	cout << "Input number of changes: ";
	cin >> m;
	cout << "The order of changes: ";
	while (temp <= m){
		cin >> change;
		for (int i = 0; i < n; i++){
			if (a[i] == change){
				pos = i;
				break;
			}
		}
		for (int i = pos; i > 0; i--){
			a[i] = a[i - 1];
		}
		a[0] = change;
		temp++;
	}
	cout << "Disk stack: ";
	for (int i = 0; i < n ;i++){
		cout << a[i] << " ";
	}
}
