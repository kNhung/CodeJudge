//Trần Danh Thiện 23127120

#include <iostream>

using namespace std;

int tinhTonguoc(int n){
    int Sum = 0;
    for ( int i = 1; i < n; i++ )
    {
        if ( n % i == 0 )
        {
            Sum += i;
        }
    }
    return Sum;
}

int main(){
    int a, b, Suma, Sumb;
    cin >> a >> b;
    if ( (a < 0) || (b < 0))
    {
        exit(0);
    }
    Suma = tinhTonguoc(a);
    Sumb = tinhTonguoc(b);
    if ( (a == Sumb) && (b == Suma) )
    {
        cout << 1;
    }
    else cout << 0;
    return 0;
}