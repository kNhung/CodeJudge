//kiem tra so ban be
//input: a, b
// output: 1 neu la so ban be, 0 neu nguoc lai
#include <iostream>

using namespace std;

void tinhTongUoc(int x, int &sum){
    for(int i = 1; i < x; ++i){
        if(x % i == 0)
            sum += i;
    }
}

void ktraSoBanBe(int a, int b){
    int sum1=0, sum2=0;
    tinhTongUoc(a, sum1);
    tinhTongUoc(b, sum2);
    if(sum1 == b && sum2 == a)
        cout << "1";
    else
        cout << "0";
}

int main(){
    int a, b;
    cin >> a >> b;

    if(a > 0 && b > 0)
        ktraSoBanBe(a, b);
    else 
        cout << "Nhapp lai";
    
    return 0;
}