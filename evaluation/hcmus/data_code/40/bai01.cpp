#include <iostream>
#define MAX 100
using namespace std;

void solve1(int a[], int n, int b[], int k){
	int pos = n - 1;
	int dem = 0;
	for (int i = 0; i < k; i++){
		for (int j = n - 1; j >= dem; j--){
			if (a[j] != b[i]) a[pos--] = a[j];
		}
		pos = n - 1;
		dem++;
		for (int i = dem - 1; i > 0; i--){
			a[i] = a[i - 1];
		}
		a[0] = b[i];
	}
}

int main(){
	int a[MAX];
	int n;
	cout << "Input number of disks: ";
	cin >> n;
	for (int i = 0; i < n; i++){
		a[i] = i + 1;
	}
	int b[MAX];
	int k;
	cout << "Input number of changes: ";
	cin >> k;
	cout << "The order of changes: ";
	for (int i = 0; i < k; i++){
		cin >> b[i];
	}
	/*int pos = n - 1;
	int dem = 0;
	for (int i = 0; i < k; i++){
		for (int j = n - 1; j >= dem; j--){
			if (a[j] != b[i]) a[pos--] = a[j];
		}
		pos = n - 1;
		dem++;
		for (int i = dem - 1; i > 0; i--){
			a[i] = a[i - 1];
		}
		a[0] = b[i];
	}*/
	solve1(a, n, b, k);
	cout << "Disk stack: ";
	for (int i = 0; i < n; i++) cout << a[i] << " ";
	return 0;
}
