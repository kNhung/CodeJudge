#include<iostream>
#include<cmath>

using namespace std;

int timSodoixung(int n);
int xoaSo(int n);

int main()
{
    int n;
    cout << "Nhap n: ";
    cin >> n;

    if(timSodoixung(n) == n)
        cout << timSodoixung(n);
    else
    {
        cout << xoaSo(n);
    }
    return 0;
}

int timSodoixung(int n)
{
    int Replacement = n;
    int Sodoixung = 0;

    while(Replacement != 0)
    {
        Sodoixung = Sodoixung * 10 + Replacement % 10;
        Replacement = Replacement / 10;
    }

    return Sodoixung;
}

int xoaSo(int n)
{
    int Sodoixung = timSodoixung(n);
    int max = 0;

    int Replacement = Sodoixung;
    int bien_kiem_tra = Replacement / 10;
    if(timSodoixung(bien_kiem_tra) == bien_kiem_tra )
        max = bien_kiem_tra;

    for(int i = 2; i <= 4; i++)
    {
        Replacement = Sodoixung;
        int he_so = pow(10,i-1);
        bien_kiem_tra = (Replacement / pow(10,i)) * he_so + Replacement % he_so;
        if(timSodoixung(bien_kiem_tra)==bien_kiem_tra) 
            if(bien_kiem_tra > max)
                max = bien_kiem_tra;
    }
    if(max!=0)  return max;

    Replacement = Sodoixung;
    while(Replacement!=0)
    {
        int x = Replacement % 100;
        if(timSodoixung(x)==x)
            if(x > max)
                max = x;
        Replacement / 10;
    }


    int a = Sodoixung;
    int x = (a/1000)*100 + (a%100)/10;
    if(timSodoixung(x)==x)
        if(x > max)
            max =x;

    a = Sodoixung;
    x = (a/1000)*100 + a%1000;
    if(timSodoixung(x)==x)
        if(x > max)
            max =x;

    a = Sodoixung;
    x = (a % 1000)/10;
    if(timSodoixung(x)==x)
        if(x > max)
            max =x;

    if(max != 0) 
        return max;
    else return -1;

}