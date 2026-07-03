#include <iostream>
#include <string>
#include <fstream>
using namespace std;
void deleteItem(int a[], int &n, int pos){
    for (int i = pos; i < n - 1; i++){
        a[i] = a[i + 1];
    }
    n--;
}
int findPos(int a[], int n, int k){
    for (int i = 0; i < n; i++){
        if (a[i] == k) return i;
    }
    return -1;
}
void insertAtFirst(int a[], int &n, int k){
    for (int i = n; i > 0; i--){
        a[i] = a[i - 1];
    }
    a[0] = k;
    n++;
}
void inputArray(int a[], int n){
    for (int i = 0; i < n; i++){
        cin >> a[i];
    }
}
void printArray(int a[], int n){
    for (int i = 0; i < n; i++){
        cout << a[i] << " ";
    }
}
void computeDiskList(int a[], int n, int b[], int m){
    for (int i = 0; i < m; i++){
        int pos = findPos(a, n, b[i]);
        deleteItem(a, n, pos);
        insertAtFirst(a, n, b[i]);
    }
}
int main(){
    int a[100];
    cout << "Input number of disks: ";
    int n; cin >> n;
    for (int i = 0; i < n; i++){
        a[i] = i + 1;
    }
    cout << "Input number of changes: ";
    int m; cin >> m;
    cout << "Input the order of changes: ";
    int b[100];
    for (int i = 0; i < m; i++){
        cin >> b[i];
    }
    computeDiskList(a, n, b, m);
    cout << "Disk stack: ";
    printArray(a, n);
}
