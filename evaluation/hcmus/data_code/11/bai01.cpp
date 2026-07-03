#include <iostream>

using namespace std;

void input(int a[], int& n){
    for (int i = 0; i < n; i++){
        a[i] = i + 1;
    }
}


int main(){
    int n;
    cout << "The number of disks: ";
    cin >> n;
    int a[n];
    input(a, n);
    int m;
    cout << "The number of changes: ";
    cin >> m;
    int b[m];
    int c[n];
    for (int i = 1; i <= m; i++){
        cout << "The order of changes: ";
        cin >> b[i];
    }
    int p = 0;
    for (int j = 0; j < m; j++){
        c[j] = b[m - j];
        cout << c[j] << " ";
    }
    for (int i = 0; i < n; i++){
        if (a[i] != b[m]){
            a[i] = i + 1;
        }
        cout << a[i] << " ";
    }

    return 0;
}
