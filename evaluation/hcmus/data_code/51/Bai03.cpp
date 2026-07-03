#include <iostream>
#include <cmath>
using namespace std;

int countLength(int n) // Count numbers of digits in int n
{
    int count = 0;
    while (n > 0)
    {
        n /= 10;
        count++;
    }
    return count;
}

int reverse(int n)
{
    int reversed = 0;
    while (n > 0)
    {
        reversed = reversed * 10 + n % 10;
        n /= 10;
    }
    return reversed;
}

bool checkSymetric(int n)
{
    if (reverse(n) == n) return true;
    else return false;
    /*if (n % int(pow(10, countLength(n - 1))) != reverse(n) % int(pow(10, countLength(n - 1))))
    {
        return -1;
    }*/
}


int main()
{
    int number;
    cout << "Please enter number to check symetric: ";
    cin >> number;
    if (number < 1000 || number >9999)
    {
        cout << "Invalid input. Out of range.\n";
        return -1;
    }
    if (checkSymetric(number))
    {
        cout << number;
    }
    else
    {
        int answer = 0;
        for (int i = 1; i <= countLength(number); i++)
        {
            if (number % int(pow(10, countLength(i- 1))) == reverse(number) % int(pow(10, countLength(i - 1))))
            {
                answer = 1;
            }
        }
        if (answer == 0) 
        {
            cout << -1 << endl;
        }
        
        {
            int number0 = number;
            int result = number;
            int d1, d4;
            d4 = number % 10;
            d1 = number / 1000;
            int d3;
            number = (number - d1 * 1000) / 10;
            if (number <= reverse(number))
            {
                d3 = number % 10;
            }
            else
            {
                d3 = number / 10;
            }
            int answer0 = d1 * 1000 + d3 * 10 + d4;
            int ans1 = number0;
            int ans2 = number0;
            //ans1 = ans1 - 100;
            if (checkSymetric(answer0))
            {
                cout << answer0 << endl;
            }
            else
                cout << -1 << endl;;
        }
    }
    return 0;
}