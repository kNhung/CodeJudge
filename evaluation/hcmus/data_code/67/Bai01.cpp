//Tinh tong cac so chan tu a den b

#include <iostream>

using namespace std;

int tinh_tongTuadenb(int& a, int& b){ 
    int sum=0, c;
    if(a>b){ // Neu a lon hon b thi dao gia tri cua a voi b
        c=a;
        a=b;
        b=c;
    }

    for(int i=a; i<=b; i++){
        if(i % 2 == 0)
            sum+=i;
    }
    return sum;
}

int main(){ 
    int a, b, sum; 
        cout << "Nhap 2 so a va b" << endl;
        cin >> a >> b;
    sum = tinh_tongTuadenb(a, b);
        cout << sum;
    return 0;
}
    