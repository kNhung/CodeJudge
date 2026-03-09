#include <iostream>
#include <cmath>

using namespace std;

int digit(int num)
{
    int cnt(0);
    while(num != 0)
    {
        num /= 10;
        cnt++;
    }
    return cnt;
}

int automorphic(int num)
{
    if(num <= 0) return -1;
    int tmp(0),tmp1(0),tmp2(0);
    tmp1 = pow(num,2);
    tmp2 = pow(10,digit(num));
    tmp = tmp1 % tmp2;
    if(tmp == num) return 1;
    else return 0;
}

int main()
{
    int num(0);
    cin >> num;
    cout << automorphic(num);
    return 0;
}
