#include<iostream>
using namespace std;
void tonguocso ( int a, int b ){
    int A = 0, B = 0 ;
    for ( int i = 1; i<= a; i++ ){
        if ( a % i == 0 ){
            A += i;
        }
    }
    for ( int j = 1; j <= b; j++ ){
        if ( b % j == 0 ){
            B += j;
        }
    }
    if ( A == B ){
        cout <<  "1" ;
    }
    else {
        cout << "0" ;
    }
}

int main (){
    int a, b;
    cin >> a >> b;
    tonguocso( a ,b );
    return 0;
}