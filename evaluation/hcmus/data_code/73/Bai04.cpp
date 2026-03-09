// 23CLC02 - 23127266 - NGUYEN ANH THU
// Bài 4
//  Kiểm tra 2 số có phải số bạn bè không
// Input: 2 tham số
//      int a, b
// Output: 1 nếu là số bạn bè
//         0 nếu không là số bạn bè

#include <iostream>

using namespace std;

int TongUoc(int number)
{
    int tong = 0;
    for (int i = 1; i < number; i++)
    {
        if (number % i == 0)
            tong += i;
    }
    return tong;
}

bool KiemTraSoBanBe(int a, int b)
{
    if (TongUoc(a) == b && TongUoc(b) == a)
        return 1;
    else
        return 0;
}

int main()
{
    int a, b;

    cin >> a >> b;
    cout << KiemTraSoBanBe(a, b);

    return 0;
}