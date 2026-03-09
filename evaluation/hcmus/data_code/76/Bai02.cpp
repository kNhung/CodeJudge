#include<iostream>
using namespace std;
void kiemtra ( int n ){
    int N ;
    int n2 = n * n ;
        if ( n < 10 ){
            N = n2 % 10 ;
        }
        if ( n >= 10 && n < 100 ){
            N = n2 % 100 ;
        }
        if ( n >= 100 && n < 1000 ){
            N = n2 % 1000;
        }
        if ( n >= 1000 && n < 10000 ){
            N = n2 % 10000;
        }
        if ( n >= 10000 && n < 100000 ){
            N = n2 % 100000;
        }
        if ( n >= 100000 && n < 1000000 ){
            N = n2 % 1000000;
        }
        if ( n >= 1000000 && n < 10000000 ){
            N = n2 % 10000000;
        }
        if ( n >= 10000000 && n < 100000000 ){
            N = n2 % 100000000;
        }
        if ( n >= 100000000 && n < 1000000000 ){
            N = n2 % 1000000000;
        }
        if ( N == n )
            cout << "1";
        else 
            cout << "0";
}
int main (){
    int n , dem = 0;
    cin >> n;
    if ( n < 0 ){
        cout << "Sai yeu cau " << endl;
    }
    else {
    kiemtra(n);
    }
    return 0;
}