#include<iostream>
using namespace std;
int const MAX = 1000;

void setArray(int a[][MAX], int &n) {
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < n; j++) {
            cin >> a[i][j];
        }
    }
}

bool checkSymmetric( int a[][MAX], int n) {
    //Kiem tra duong cheo chinh//
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (a[i][j] != a[j][i]) {
                return false;
            }
        }
    }

    //Kiem tra duong cheo phu//
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (a[i][j] != a[n - j - 1][n - i - 1]) {
                return false;
            }
        }
    }

    return true;
}

int main() {
    int a[1000][1000];
    int n;
    cin >> n;
    setArray(a,n);
    if(checkSymmetric(a,n) == true) {
        cout << "True";
    } else {
        cout << "False";
    }
    
    return 0; 
}