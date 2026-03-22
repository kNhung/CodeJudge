#include <iostream>
using namespace std;

void printArr(int a[], int n) {
    for (int i = 0; i < n; i++) {
        cout << a[i] << " ";
    }
}
void pushToFirst(int a[], int n, int k) {
    int buffer = a[k];
    for (int i = k; i > 0; i--) {
        a[i] = a[i - 1];
    }
    a[0] = buffer;
}

void pushDisc(int a[], int n, int x) {
    for (int i = 0; i < n; i++) {
        if (a[i] == x) {
            pushToFirst(a, n, i);
            break;
        }
    }
}

int main() {
    int n;
    int k;
    int a[10001];
    int c[10001];
    cout << "Input number of disks: "; cin >> n;
    for (int i = 0; i < n; i++) {
        a[i] = i + 1;
    }
    cout << "Input number of changes: "; cin >> k;
    cout << "The order of changes: ";
    for (int i = 0; i < k; i++) {
        cin >> c[i];
        pushDisc(a, n, c[i]);
    }
    cout << "Disk stack: ";
    printArr(a, n);
    return 0;
}

