// De bai:
//  Câu 4. (2đ) Một cặp số nguyên dương được gọi là số bạn bè nếu tổng các ước
//  số của số này (không tính bản thân số đó) bằng chính số kia và ngược lại. Viết
//  chương trình nhập vào hai số nguyên dương a và b, kiểm tra xem hai số nhập
//  vào có phải là số bạn bè hay không. In 0 nếu không phải số bạn bè, ngược lại,
//  trả về 1.

#include <iostream>
#include <cmath>

using namespace std;

int getSum(int n)
{
    int s = 0;
    for (int i = 1; i < n; i++)
    {
        if (n % i == 0)
            s += i;
    }
    return s;
}

int isFriend(int a, int b)
{
    if (getSum(a) == b && getSum(b) == a)
        return 1;
    return 0;
}
int main()
{
    int a, b;
    cin >> a >> b;
    cout << isFriend(a, b);

    return 0;
}