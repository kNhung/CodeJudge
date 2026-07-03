#include <iostream>
#include <cstring>
using namespace std;

#define MAX 100

void ChuoiDaXoa(char C[MAX]){
    int n = strlen(C);
    while (true){
        int i = 0;
        while (i < n - 1){
            if (C[i] == C[i+1]){
                for (int j = i; j < n - 2; j++)
                    C[j] = C[j + 2];
                n -= 2;
            }
            i++;
        }
        bool ok = true;
        for (int i = 0; i < n - 1; i++)
            if (C[i] == C[i + 1]){
                ok = false;
                break;
            }
        if (ok)
            break;
    }
    for (int i = 0; i < n; i++)
        cout << C[i];
}

int main(){
    char C[MAX];
    cin >> C;
    ChuoiDaXoa(C);
    cout << endl;
    return 0;
}
