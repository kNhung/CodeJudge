#include <iostream>

using namespace std;

int sumDivisor(int num)
{
    int sum(0);
    for(int i = 1;i < num;i++)
        if(num % i == 0) sum += i;
    return sum;
}

int neighborNum(int num1,int num2)
{
    if(num1 <= 0 || num2 <= 0) return 0;
    int tmp1 = sumDivisor(num1),tmp2 = sumDivisor(num2);
    if(tmp1 = tmp2) return 1;
    else return 0;
}

int main()
{
    int num1(0),num2(0);
    cin >> num1 >> num2;
    cout << neighborNum(num1,num2);
    return 0;
}
