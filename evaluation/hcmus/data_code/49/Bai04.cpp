/*
2đ) Một cặp số nguyên dương được gọi là số bạn bè nếu tổng các ước
số của số này (không tính bản thân số đó) bằng chính số kia và ngược lại. Viết
chương trình nhập vào hai số nguyên dương a và b, kiểm tra xem hai số nhập
vào có phải là số bạn bè hay không. In 0 nếu không phải số bạn bè, ngược lại,
trả về 1.
VD:
Input:
Nhập a: 220
Nhập b: 284
Output: 1
Giải thích:
Tổng các ước số của 220 là:
1 + 2 + 4 + 5 + 10 + 11 + 20 + 22 + 44 + 55 + 110 = 284
Tổng các ước số của 284 là:
1 + 2 + 4 + 71 + 142 = 220
=> 220 và 284 là số bạn bè
*/

#include <iostream>

using namespace std;

int sumOfDivisor(int n)
{
    int sum = 0;
    for (int i = 1; i < n; i++)
    {
        if (n % i == 0)
        {
            sum = sum + i;
        }
    }
    return sum;
}

int isFriend(int a, int b)
{
    int sumOfA = 0, sumOfB = 0;
    sumOfA = sumOfDivisor(a);
    sumOfB = sumOfDivisor(b);

    if (sumOfA == b && sumOfB == a)
        return 1;
    return 0;
}

int main()
{
    int a, b;
    do
    {
        cin >> a >> b;
    } while (a <= 0 || b <= 0);

    cout << isFriend(a, b) << endl;

    return 0;
}