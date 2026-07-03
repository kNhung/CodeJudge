// De bai:
//  Câu 2. (3đ) Một số automorphic là một số tự nhiên mà bình phương của nó chứa
//  số kết thúc bằng chính nó. Viết chương trình nhập vào một số nguyên dương n
//  (n > 0), kiểm tra n có phải là số automorphic hay không. In ra 1 nếu n là số
//  automorphic, ngược lại, in ra 0.
//  VD:
//  Input: 25
//  Output: 1
//  (số 25 là một số Automorphic vì bình phương của nó là 625 và 625 kết
//  thúc bằng chính số 25)

#include <iostream>
#include <cmath>
using namespace std;

int getNumberOfDigits(int num)
{
    int count = 0;
    while (num != 0)
    {
        num /= 10;
        count++;
    }
    return count;
}

int isAutomorphic(int num)
{
    int power = pow(10, getNumberOfDigits(num));
    power++;
    if(num < 10)
        power = 10;
    int last = (num * num) % power;
    if (num == last)
        return 1;
    return 0;
}
int main()
{
    int n;
    cin >> n;
    
    cout << isAutomorphic(n);

    return 0;
}