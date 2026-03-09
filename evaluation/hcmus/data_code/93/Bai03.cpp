#include <iostream>
#include <math.h>
using namespace std;
bool Doixung(int n){
    int Doixung = 0, m = n;
    while(n != 0){
        Doixung = Doixung * 10 + n % 10;
        n /= 10;
    }
    if(Doixung == m){
        return true;
    }
    else return false;
}
void check(int n){
	int donvi = n % 10, j = 0, m = 0, k = 1;
    for(int i = 10; ; i*=10){
        int ans = (n / i) * k + donvi*j;
        if(Doixung(ans)){
            if(m < ans){
                m = ans;
            }
        }
        j = 1;
        k *= 10;
    }
    if(m != 0){
        cout << m;
    }
    else {
    	cout << -1;
	}
}   
int main(){
    int n;
    cin >> n;
    if(Doixung(n)){
    	cout << n << endl;
	}
    check(n);
    return 0;
}
