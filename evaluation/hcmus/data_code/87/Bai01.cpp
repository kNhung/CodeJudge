#include <iostream>

using namespace std;

/*
Tinh tong cac chu so chan trong doan [a,b] cho truoc
*/

int tinhTong(int n, int m)
{
    int sum = 0;
    for (int i = n; i <= m; i++)
    {
        if (i % 2 == 0)
            sum += i;
    }
    return sum;
}

int main()
{
    int n, m;
    cin >>n;
    cin >>m;
    
    if (n <= m)
        cout <<tinhTong(n,m);
    else 
        cout <<"Input again";
    return 0;
}