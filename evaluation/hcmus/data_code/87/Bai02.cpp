#include <iostream>

using namespace std;

/*
Kiem tra 1 so co phai la so Automorphic hay khong
*/

int demSo(int n)
{
    int cnt = 1;
    while(n)
    {
        cnt = cnt * 10;
        n /= 10;
    }
    return cnt / 10;
}
int checkAutomorphic(int n)
{
    int m = n * n;
    int k = 10 * demSo(n);
    
    if (m % k == n)
        return 1;
    else return 0;
}

int main()
{
    int n;
    cin >>n;

    cout <<checkAutomorphic(n);
    return 0;
}