// 23CLC02 - 23127266 - NGUYEN ANH THU
// Bài 1
// Tổng các số chẵn trong đoạn từ [a,b]
// Input: 2 số nguyên int a, b
// Output: 1 tham số int sum (tổng các số chẵn [a,b])

#include <iostream>

using namespace std;

void solve()
{
    int a, b, sum(0);

    cin >> a >> b;

    for (int i = a; i <= b; i++)
        if (i % 2 == 0)
            sum += i;

    cout << sum;
}

int main()
{
    solve();
    return 0;
}