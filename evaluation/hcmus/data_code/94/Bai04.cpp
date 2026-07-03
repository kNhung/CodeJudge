#include <iostream>

using namespace std ;

//ham ktra tinh tong cac uoc tru chinh so do
long long Sum_Divisor(long long n ){

    long long sumdiv = 0 ;

    for(long long i = 1 ; i < n ; i ++ ){

        if(n%i == 0){
            if(i == n / i ){
                sumdiv += i + (n / i) ;
            }
            else 
            sumdiv += i ;
        }

    }
    
    return sumdiv;
}

//viet ham kiem tra hai so ban be
long long Number_Friend(long long a , long long b){

    if(Sum_Divisor(a)== b && Sum_Divisor(b)== a){
        return 1;
    }
    return 0;
}

int main(){

    long long a,b ;
    cin>>a>>b ;

    if( Number_Friend(a, b) ){
        cout<<1;
    }
    else {
        cout<<0;
    }
    return 0;

}