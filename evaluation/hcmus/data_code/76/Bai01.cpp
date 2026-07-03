#include<iostream>
using namespace std;
void tongsochan ( int a, int b ){
    int tong = 0;
    for ( int i = a; i <= b; i++){
        if ( i % 2 == 0 ){
            tong += i ;
        }
    }
    cout << "Tong cac so chan trong khoang tu " << a << " va " << b << " la: " << tong << endl;
}
int main (){
    int a, b;
    cin >> a >> b;
    tongsochan ( a, b );
    return 0;
}
