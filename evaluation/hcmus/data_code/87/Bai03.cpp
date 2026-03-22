#include <iostream>

using namespace std;

/*
Viet chuong trinh kiem tra so doi xung 
*/

int soDoiXung(int n)
{
    int rev = 0, temp = n;
    while(n)
    {
        rev = rev * 10 + n % 10;
        n /= 10;
    }
    return rev == temp;
}
int ktraSo(int n)
{
    if (soDoiXung(n)) return n;

    if (n % 10 == n / 1000)  //ktra so dau va so cuoi cua so n
    {
        int k = n % 10;    //gan chu so cuoi cua n vao k
        n /= 10;    
        int m = n % 100;     //gan 2 so giua cua n cho m
        int p = m % 10;    //gan so hang don vi cua m cho p

        int newNum;
        if (p < m / 10)  //so sanh so o hang don vi va so o hang chuc cua m
            newNum = m / 10;
        else    
            newNum = p;
            
        newNum = k * 100 + newNum * 10 + k;
        return newNum;
    }
    else return -1;
}

int main()
{
    int n;
    cin >>n;
    if (n >= 1000 && n <= 9999)
        cout <<ktraSo(n);
    else
        cout <<"Input again";
    
    return 0;
}