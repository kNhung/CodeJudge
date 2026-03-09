#include <iostream>

using namespace std;

int countDigit(int n)
{
    int count = 0;
    while (n > 0)
    {
        n = n / 10;
        count++;
    }
    return count;
}

int isAutomorphic(int n)
{
    long int sqrOfN = n * n;
    int digitNumSqr = countDigit(n);
    long int level = 10;
    for (int i = 1; i <= digitNumSqr - 1; i++)
    {
        level = level * 10;
    }

    if (sqrOfN % level == n)
        return 1;
    return 0;
}

int main()
{
    int n;
    do
    {
        cin >> n;
    } while (n <= 0);

    cout << isAutomorphic(n) << endl;

    return 0;
}