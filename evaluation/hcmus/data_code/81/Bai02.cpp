#include <iostream>
#include <cmath>

using namespace std;

void ktraAutomorphic(int n, int &result){
    int binhPhuong = floor(pow(n, 2));
    int i  = 0;
    while(n > 0){
        n = n / 10;
        i++;
    }
    float chiaDu = floor(pow(10, i));
    int k = chiaDu;
    result = binhPhuong % k;
}

int main(){
    int n, result = 0;

    cin  >> n;

    if(n <= 0)
        cout << "Nhap lai";
    ktraAutomorphic(n, result);
    if(result == n)
        cout << "1";
    else 
        cout << "0";


    return 0;
}