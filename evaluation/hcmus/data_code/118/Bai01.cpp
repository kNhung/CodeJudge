#include<iostream>
#define MAX 50
using namespace std;



bool ktraDoiXungDuongCheochinh(int a[][MAX], int n){
    for(int i = 0; i < n; ++i){
        for(int j = 0; j < n; ++j){
            if(i != j){
                if(a[i][j] != a[j][i]) return false;
            }
        }
    }
    return true;
}
/*
bool ktreaDoixungDuongCheoPhu(int a[][MAX], int n){
    for(int i = 0; i < n; ++i){
        for(int j = 0; j < n; ++j){
            if()
        }
    }
    for(int i = 0; i < n; ++i){
        for(int j = n - 1; j > 0; --j){
            cout << a[i][j] << " ";
        }
    }

}
*/
bool ktraDoixung(int a[][MAX],int n){
    if(ktraDoiXungDuongCheochinh(a,n) == 1 && ktreaDoixungDuongCheoPhu(a,n) == 1) return true;
    else return false;
}
int main(){
    int n;
    cout << "Nhap n: ";
    cin >> n;
    int a[MAX][MAX];

    for(int i = 0; i < n; ++i){
        for(int j = 0; j < n; ++j){
            cin >> a[i][j];
        }
    }

    for(int i = 0; i < n; ++i){
        for(int j = 0; j < n; ++j){
            cout << a[i][j] << " ";
        }
        cout << endl;
    }
    //cout << ktraDoiXungDuongCheochinh(a,n);
 
    return 0;
}