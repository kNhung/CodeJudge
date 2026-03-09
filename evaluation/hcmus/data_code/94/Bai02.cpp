#include <iostream>
#include <cmath>

using namespace std ;

//viet ham tinh so chu so cua n 
long long Number(long long n ){

    long long cnt = 0; 
    while(n != 0 ){
        n /= 10;
        ++cnt;
    }

    return cnt;

}
//viet ham kiemtra so automorphic 
long long Check_Automorphic(long long n ){

    long long tmp = Number(n);
    long long qh = pow(10 , tmp -1 );

    if( (n * n - n ) % qh ==0 )
    return 1;

    return 0;

}

int main (){
    long long n ;
    cin>>n;

    if( Check_Automorphic(n) ){
        cout<<1;
    }
    else{ 
    cout<<0;
    }

    return 0;
    
}