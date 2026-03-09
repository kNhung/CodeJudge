#include<iostream>
using namespace std;

int timSoDoiXung(int n)
{
    int soDoiXung = 0, chu_so;

    while(n != 0)
    {
        chu_so = n % 10;
        soDoiXung = soDoiXung * 10 + chu_so;
        n /= 10;
    }
    return soDoiXung;
}

bool ktraSoDoiXung(int n)
{
    if(timSoDoiXung(n) == n)
        return true;
    return true;
}

int main()
{
    int n;
    do {
        cin >> n;
        if (n < 1000 || n > 9999);
    } while( n < 1000 || n > 9999);

    if(ktraSoDoiXung(n) == true)
        cout << timSoDoiXung(n) << endl;
    return 0;
}