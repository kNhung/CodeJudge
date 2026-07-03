#include <iostream>
#include <cstring>
#include <cmath>
using namespace std;
long long a[1000][1000];
bool chinh(int n){
    for(int i = 0; i < n; i++){
        for(int j = 0; j < i; j++){
            if(a[i][j] != a[j][i]){
                return false;
            }
        }
    }
    return true;
}
bool phu(int n){
    for(int i = n - 1; i >= 0; i--){
        for(int j = i - 1; j >= 0; j--){
            if(a[i][j] != a[n - 1 -j][n - 1 - i]){
                return false;
            }
        }
    }
    return true;
}
int main(){
    int n;
    cin >> n;
    int x = sqrt(n);
    for(int i = 0; i < x; i++){
        for(int j = 0; j < x; j++){
            cin >> a[i][j];
        }
    }
    if(chinh(x) || phu(x)){
        cout << "True";
    }
    else cout << "False";
    return 0;
}