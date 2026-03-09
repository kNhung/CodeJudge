#include <iostream>
#include <cmath>

using namespace std;

int main(){
	int n, m, a[10002] = {}, pos[10000] = {};
	cout << "Input number of disks: ";
	cin >> n;
	for (int i = 1; i <= n; i++){
		a[i] = i;
		pos[i] = i;
	}
	cout << "Input number of changes: ";
	cin >> m;
	cout << "The order of changes: ";
	for(int j = 0; j < m; j++){
		int disknum;
		cin >> disknum;
		for(int i = pos[disknum] - 1; i > 0; i--){
			a[i + 1] = a[i];
			pos[a[i]] = i + 1;
		}
		a[1] = disknum;
		pos[disknum] = 1;
	}
	cout << "Disk stack: ";
	for(int i = 1; i <= n; i++){
		cout << a[i] << " ";
	}
	return 0;
}
