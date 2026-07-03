// 23CLC02 - 23127266 - NGUYEN ANH THU
//  Bài 2
// Kiểm tra n có phải số Automorphic không
// Input: 1 tham số int n
// Output: 1 nếu là số Automorphic,
//      ngược lại 0

#include <iostream>
#include <cmath>
#define ll long long
using namespace std;

// Hàm tìm số
bool FindNumber(ll finalNumber, ll n)
{
    ll Number(0);
    ll base = 1;

    while (n >= base)
    {
        ll temp = n % base;

        if (temp == finalNumber)
            return 1;

        base *= 10;
    }

    return 0;
}

// Hàm kiểm tra số
bool CheckAutomorphic(ll n)
{
    if (n == 1)
        return 1;

    ll temp = sqrt(n);

    // nếu n là số chính phương
    if (temp * temp == n)
    {
        // Tìm số tận cùng bằng n
        if (FindNumber(temp, n))
            return 1;
        else
            return 0;
    }

    return 0;
}

void solve()
{
    ll n;

    cin >> n;

    n = n * n;

    cout << CheckAutomorphic(n);
}

int main()
{
    solve();

    return 0;
}