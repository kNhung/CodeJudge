#include <iostream>
#include <cstring>
#include <cmath>
using namespace std;

bool dx(int a[][100], int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if(a[i][j] != a[j][i]) return false;
        }
    }
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (a[i][j] != a[n - 1 - j][n - 1 - i]) return false;
        }
    return true;
    } 
}

int main() {
    int t;
    cin >> t;
    for (int k = 0; k < t; k++) {
        int n;
        cin >> n;
        int a[100][100];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                cin >> a[i][j];
            }
        }
        
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                cout << a[i][j] << " ";
            }
        }
        if(dx(a, n) == true) {
            cout << "True";
        } else {
            cout << "False";
        }
    }
    
    return 0;
}






