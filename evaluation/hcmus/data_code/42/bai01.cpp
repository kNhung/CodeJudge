#include <iostream>
#include <cmath>
#include <cstring>
#include <string>
#include <stdlib.h>

using namespace std;

void layRa1Dia(int a[], int n, int dia){
    int vitri;
    for (int i = 0; i < n; i++){
        if (a[i] == dia){
            vitri = i;
        }
    }
    int temp = a[vitri];
    for (int i = vitri; i > 0; i--){
        a[i] = a[i-1];
    }
    a[0] = temp;

}

int main(){
    int a[10001], n;
    cout << "Input number of disks: ";
    cin >> n;
    int dem = 1;
    for (int i = 0; i < n; i++){
        a[i] = dem;
        dem++;
    }

    int change;
    cout << "Input number of changes: ";
    cin >> change;

    int diaLayRa[change];
    cout << "The order of changes: ";
    for (int i = 0; i < change; i++){
        cin >> diaLayRa[i];
    }

    for (int i = 0; i < change; i++){
        layRa1Dia(a,n,diaLayRa[i]);
    }
    cout << "Disk stack: ";
    for (int i = 0; i < n; i++){
        cout << a[i] << " ";
    }
    return 0;
}

