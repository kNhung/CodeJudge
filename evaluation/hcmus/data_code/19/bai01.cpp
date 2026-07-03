#include <iostream>
#include <algorithm>

using namespace std;

void updateDiskStack(int diskStack[], int n, int diskNumber) {
    // Tìm vị trí của đĩa trong chồng đĩa
    auto it = find(diskStack, diskStack + n, diskNumber);

    // Di chuyển đĩa đó lên trên cùng
    rotate(diskStack, it, it + 1);
}

int main() {
    int n; // Số lượng đĩa nhạc
    int m; // Số lần nghe đĩa
    int diskNumber; // Số đĩa được nghe

    // Nhập số lượng đĩa nhạc và số lần nghe đĩa
    cout << "Input number of disks: ";
    cin >> n;
    cout << "Input number of changes: ";
    cin >> m;

    int diskStack[10000]; 

    // Khởi tạo chồng đĩa ban đầu
    for (int i = 0; i < n; i++) {
        diskStack[i] = i + 1;
    }

    // Nhập và xử lý các lần nghe đĩa
    cout << "The order of changes: ";
    for (int i = 0; i < m; i++) {
        cin >> diskNumber;
        updateDiskStack(diskStack, n, diskNumber);
    }

    // Hiển thị chồng đĩa cuối cùng
    cout << "Disk stack: ";
    for (int i = 0; i < n; i++) {
        cout << diskStack[i] << " ";
    }

    return 0;
}
