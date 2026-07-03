// Đề bài: Một cặp số nguyên dương được gọi là số bạn bè nếu tổng các ước số của số này (không tính bản thân số đó) bằng chính số kia và ngược lại. Viết chương trình nhập vào hai số nguyên dương a và b, kiểm tra xem hai số nhập vào có phải là số bạn bè hay không.
// In 0 nếu không phải số bạn bè, ngược lại, trả về 1.

#include <iostream>
using namespace std;

int TongUocSo(int n){
    int tong = 0;
    for (int i = 1; i < n; i++)
        if (n % i == 0)
            tong += i;
    return tong;
}

bool SoBanBe(int a, int b){
    if (TongUocSo(a) == b && TongUocSo(b) == a)
        return true;
    return false;
}

int main(){
    int a, b;
    cin >> a >> b;
    cout << SoBanBe(a, b) << endl;
    return 0;
}