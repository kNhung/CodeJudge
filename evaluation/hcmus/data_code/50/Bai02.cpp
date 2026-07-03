// Bai02.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
using namespace std;

void nhap(int& n)
{
    cin >> n;
    while (n < 1)
    {
        cin >> n;
    }
}

int count(int n)
{
    int cnt = 0;
    while (n != 0)
    {
        cnt++;
        n /= 10;
    }
    return cnt;
}

int isAutomorphic(int n)
{
    int temp = n * n;
    int cnt = count(temp);
    int level = 1;
    for (int i = 1; i <= cnt; i++)
    {
        level = level * 10;
        if (temp % level == n)
        {
            return 1;
        }
    }
    return 0;
}

int main()
{
    int n;
    nhap(n);
    cout << isAutomorphic(n) << endl;
    return 0;
}

