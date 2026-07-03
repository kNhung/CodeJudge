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

int reverseNum(int num)
{
    int tmp(0),i(0);
    while(num != 0)
    {
        tmp = tmp * pow(10,i) + num % 10;
        num /= 10;
    }
    return tmp;
}

int deleteNum(int num,int pos,int am)
{
    int tmp(0),ans(0),tmp1 = pow(10,pos),tmp2 = pow(10,pos - am);
    tmp = num % tmp1;
    ans = num / tmp1 * tmp2 + tmp % tmp2;
    return ans;
}

int check(int num)
{
    if(num < 1000 || num > 9999) return -1;

    for(int i = 1;i <= digit(num);i++)
    {
        for(int j = 1;i <=)
    }

}

int main()
{
    int num(0),am(0);
    cin >> num;
    cout << check(num);
    return 0;
}
