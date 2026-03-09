//Trần Danh Thiện 23127120

#include <iostream>

using namespace std;

bool isSochan(int n){
    if (n % 2 == 0)
    {return true;}
    else return false;
}
int main(){
    int a, b, Sum = 0;
    cin >> a >> b;
    if ( a < 0 || b < 0 || a > b)
    {
        exit(0);
    }
    for (int i = a; i <= b;i++)
    {
        if (isSochan(i))
        {
            Sum += i;
        }
    }
    cout << Sum;
    return 0;
}