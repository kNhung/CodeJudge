//Trần Danh Thiện 23127120

#include <iostream>

using namespace std;

int main(){
    int n = 1, a, b, c;
    cin >> a;
    while ( n <= a){
        n *= 10;
    }
    b = a*a;
    c = b % n;
    if ( c == a)
    {
        cout << 1;
    }
    else cout << 0;
    return 0;
}