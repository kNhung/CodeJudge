
#include <iostream>
using namespace std;

// Hàm in mảng đĩa
void printDiskStack(int diskStack[], int n) {
	cout << "Disk stack: ";
	for (int i = 0; i < n; ++i)
	{
		cout << diskStack[i] << " ";
	}
	cout << endl;
}

// Hàm di chuyển đĩa lên đầu chồng
void moveDiskToTop(int diskStack[], int n, int diskToMove) {
	// Tìm vị trí của đĩa cần di chuyển
	int index = -1;
	for (int i = 0; i < n; ++i)
	{
		if (diskStack[i] == diskToMove)
		{
			index = i;
			break;
		}
	}

	// Nếu đĩa được tìm thấy, di chuyển nó lên đầu chồng
	if (index != -1) {
		for (int i = index; i > 0; --i) 
		{
			int temp = diskStack[i];
			diskStack[i] = diskStack[i - 1];
			diskStack[i - 1] = temp;
		}
	}
}

int main() {
	int n, m;
	cout << "Input number of disks: ";
	cin >> n;

	int diskStack[10000];
	for (int i = 0; i < n; ++i) {
		diskStack[i] = i + 1;
	}

	cout << "Input number of changes: ";
	cin >> m;

	cout << "The order of changes: ";
	for (int i = 0; i < m; ++i) 
	{
		int change;
		cin >> change;

		moveDiskToTop(diskStack, n, change);
	}
	printDiskStack(diskStack, n);

	return 0;
}
