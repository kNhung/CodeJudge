/*
Số nguyên n gọi là số đối xứng là số có từ 2 chữ số trở lên và nếu
đọc từ trái qua phải, hay từ phải qua trái đều được số giống nhau. Viết chương
trình nhập vào một số nguyên dương n (1000 <= n <= 9999), in ra số đối xứng
lớn nhất có thể tạo ra được bằng việc xóa con số bất kì trong n. Lưu ý: số lượng
con số bị xóa chưa được xác định.
VD:
Input: 1231
Output: 121 (xóa 1 chữ số 3)
*/

#include <iostream>
#include <cmath>

using namespace std;

int countDigit(int n)
{
    int count = 0;
    while (n != 0)
    {
        n = n / 10;
        count++;
    }
    return count;
}

bool isPalin(int n)
{
    int reverse = 0;
    int ori = n;
    while (n != 0)
    {
        reverse = reverse * 10 + n % 10;
        n /= 10;
    }
    if (ori == reverse)
        return true;
    return false;
}

int inverseNum(int n)
{
    int revNum = 0;
    while (n != 0)
    {
        int temp = n % 10;
        revNum = revNum * 10 + temp;
        n = n / 10;
    }
    return revNum;
}

int deleteDigit(int n, int i)
{
    /*int digitNum = countDigit(n);
    int revNum = inverseNum(n);
    int count = 0;
    int newRev = revNum, newN = n;
    while (newN != 0 && newRev != 0)
    {
        int temp1 = newN % 10;
        int temp2 = newRev % 10;
        count++;
        if (temp1 > temp2)
        {
            int divide = pow(10, count);
            int tNum = n;
            // cout << n << endl;
            // cout << divide << endl;
            revNum = revNum - revNum % (divide * 10);
            // cout << revNum << endl;
            revNum = revNum / 10;
            // cout << revNum << endl;
            revNum = revNum + tNum % divide;
            // cout << revNum << endl;
        }
        newN = newN / 10;
        newRev = newRev / 10;
    }
    return revNum;
    */
    int result = 0, remain = 1;
    while (n != 0)
    {
        if (n % 10 != i) // i gonna be digit num
        {
            result += (n % 10) * remain;
            remain = remain * 10;
        }
        n /= 10;
    }
    return result;
}

int largestPalin(int n)
{
    int largest = 0;
    for (int i = 0; i <= 9; i++)
    {
        int temp = deleteDigit(n, i);
        if (isPalin(temp) == true && temp > largest)
        {
            largest = temp;
        }
    }
    if (largest == 0)
        return -1;
    return largest;
}

int main()
{
    int n;
    do
    {
        cin >> n;
    } while (n < 1000 || n > 9999);

    cout << largestPalin(n) << endl;

    return 0;
}