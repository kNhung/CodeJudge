// Kiem tra cap so ban be

#include <iostream>

using namespace std;

int tong_uoc(int& a){ // Tim tong cac uoc so ( khong tinh ban than so do )
    int sum=0;
    for(int i=1; i<=a/2; i++){
        if(a % i == 0)
            sum += i;
    }
    return sum;
}

int main(){
    int c, d; 
        cout << "Nhap hai so nguyen duong" << endl;
        cin >> c >> d;
    if(c <= 0 || d <=0)
        cout << "Nhap sai";
    else{
        int sum_c=tong_uoc(c);
        int sum_d=tong_uoc(d);
        
        if(sum_c == d && sum_d == c)
            cout << "1";
        else    
            cout << "0";
    }
    return 0;
}