#include<iostream>
#include<cmath>

using namespace std;

bool isAutomorphic(int n);
void check(int &n);

int main()
{
    int n;
    cout << "Nhap n: ";
    cin >> n;

    check(n);

    if(isAutomorphic(n) == true)
        cout << 1;
    else   
        cout << 0;
    
    return 0;
}

bool isAutomorphic(int n)
{
    int Replacement = n;
    int count = 0;

    while(Replacement != 0)
    {
        count++;
        Replacement = Replacement / 10;
    }

    int he_so = pow(10, count);
    if( ((n * n) % he_so) == n)
        return true;
    else
        return false;
}

void check(int &n)
{
    while(n <= 0)
    {
        cout << "Khong hop le!" << endl;
        cout << "Moi nhap lai n: ";
        cin >> n;
    }
}
