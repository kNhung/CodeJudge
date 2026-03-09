// 23CLC02 - 23127266 - NGUYEN ANH THU
// Bài 3
// Tìm số đối xứng lớn nhất (khi xóa chữ số bất kỳ trong n)
// Input: 1 tham số int n (1000 < n < 9999)
// Output: 1 tham số int result (số đối xứng lớn nhất)

#include <iostream>

using namespace std;

// Hàm kiểm tra số đối xứng
bool CheckPalindome(int number)
{
    int result(0);

    int temp = number;
    while (temp > 0)
    {
        result = result * 10 + (temp % 10);

        temp /= 10;
    }

    if (result == number)
        return 1;

    return 0;
}

// Hàm tìm số lớn nhất
int findMax(int number1, int number2)
{
    if (number1 >= number2)
        return number1;
    else
        return number2;
}

// Hàm tìm kết quả
// Xóa các chữ số trong n
int FindNumber(int n)
{
    int result = -1;
    if (CheckPalindome(n))
        return n;
    // Xóa 1 chữ số
    int exponent1 = 1;
    for (int i = 1; i <= 4; i++)
    {
        int number1 = (n / (exponent1 * 10)) * exponent1 + n % exponent1;
        exponent1 *= 10;

        if (!CheckPalindome(number1))
        {
            // Xóa 2 chữ số
            int exponent2 = 1;
            for (int j = 1; j <= 3; j++)
            {
                int number2 = (number1 / (exponent2 * 10)) * exponent2 + number1 % exponent2;
                exponent2 *= 10;

                if (CheckPalindome(number2))
                    result = findMax(result, number2);
            }
        }
        else
            result = findMax(result, number1);
    }

    return result;
}

// Hàm giải quyết yêu cầu bài toán
void solve()
{
    int n;
    cin >> n;

    cout << FindNumber(n);
}

int main()
{
    solve();

    return 0;
}