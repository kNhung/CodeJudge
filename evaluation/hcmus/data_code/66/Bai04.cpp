#include<iostream>
using namespace std;

//Ham tinh tong cac uoc//
int tinhTongUoc (int n) 
{
    int tong = 0;
    for (int i = 1; i < n; i++) {
        if(n % i == 0)
            tong += i;
    }
    return tong;
}

int main()
{
    int a, b;
    cin >> a >> b;
    //Goi ham tinh tong cac uoc va so sanh voi so con lai//
    if (tinhTongUoc(a) == b && tinhTongUoc(b)== a)
        cout << 1;
    else cout << 0;

    return 0;
   
}