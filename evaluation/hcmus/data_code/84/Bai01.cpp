#include <iostream>

using namespace std;

int sumEven(int lnum,int rnum)
{
    int sum(0);
    for(int i = lnum;i <= rnum;i++)
        if(i % 2 == 0) sum += i;
    return sum;
}

int main()
{
    int a(0),b(0);
    cin >> a >> b;
    cout << sumEven(a,b);
    return 0;
}
