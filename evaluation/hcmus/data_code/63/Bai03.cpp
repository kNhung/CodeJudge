//Trần Danh Thiện 23127120

#include <iostream>
#include <math.h>

using namespace std;

bool ktra(int n){
    int a = 0,b = 1, cnt = 0;
    int n1= n;
    while ( b <= n )
    {
        b = b * 10;
        cnt++;
    }
    b /= 10;
    for ( int i = b; i >= 1; i/=10)
    {
        int x;
        x = n1 % 10;
        a = a + x*i;
        n1 = n1 / 10;
    }
    if ( a == n )
    {
        return true;
    }
    else return false;
}
int xoaChuso(int n, int Chuso, int vtri){
    int a, b = 0;
    int c = pow(10,vtri);
    int d = pow(10,vtri - Chuso);
    int e = pow(10, vtri - Chuso);
    b = n % d;
    n = n / c;
    n = n * e + b;
    return n;
}
int main(){
    int n, max = -1;
    cin >> n;
    if ( ( n < 1000 ) || ( n > 9999 ))
    {
        exit(0);
    }
    for ( int i = 0; i <= 2; i++)
    {
        for ( int j = 4; j >= i; j-- )
        {
            int x;
            x = xoaChuso(n, i, j);
            if ( ktra(x))
            {
                if ( max <= x )
                {
                    max = x;
                }
            }
        }
    }
    cout << max;
    return 0;
}