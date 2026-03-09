#include <iostream>

using namespace std;

int main(){
    int n;
    cin >> n;

    int digit1 = n / 1000;
    int digit2 = (n / 100) % 10;
    int digit3 = (n % 100) / 10;
    int digit4 = n % 10;
    
    int result = 0;
    if (digit1 == digit4){
        if (digit2 == digit3)
            result = n;
        else if (digit2 > digit3)
            result = digit1*100 + digit2*10 + digit4;
        else
            result = digit1*100 + digit3*10 + digit4;
    } else if (digit1 == digit3)
        if ((digit2 ==  digit4) && digit1 < digit2)
            result = n % 1000;
        else
            result = n/10;
    else if (digit2 == digit4)
        result = n % 1000;
    else if (digit1 == digit2)
        result = n / 100;
    else if (digit3 == digit4)
        result = n % 100;
    else if (digit2 == digit3)
        result = digit2*10 + digit3;
    else result = -1;
   
    cout << result;

    return 0;
}