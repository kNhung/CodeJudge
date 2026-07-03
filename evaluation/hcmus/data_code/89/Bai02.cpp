#include <iostream>

using namespace std;

int checkAutomorphic(int n) {
    int i = n * n;
    int temp = 0;
    for (int j = 10; j <= i; j *= 10) {
        temp = i % j;
        if (temp == n) {
            return 1;     
        }
    }
    return 0;
}

int main() {
    int n; 
    cout << "Nhap: ";
    cin >> n;

    int Automorphic = checkAutomorphic(n);
    cout << Automorphic << endl;;

    return 0;
}