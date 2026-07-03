// Câu 3. (2đ)
//  Số nguyên n gọi là số đối xứng là số có từ 2 chữ số trở lên và nếu
//  đọc từ trái qua phải, hay từ phải qua trái đều được số giống nhau. Viết chương
//  trình nhập vào một số nguyên dương n (1000 <= n <= 9999), in ra số đối xứng
//  lớn nhất có thể tạo ra được bằng việc xóa con số bất kì trong n. Lưu ý: số lượng
//  con số bị xóa chưa được xác định.
//  VD:
//  Input: 1231
//  Output: 121 (xóa 1 chữ số 3)
//  Input: 1221
//  Output: 1221(Xóa 0 chữ số)
#include <iostream>
#include <cmath>

using namespace std;
int getRevert(int n)
{
    int answer = 0;
    while (n != 0)
    {
        answer += n % 10;
        answer *= 10;
        n /= 10;
    }
    return answer / 10;
}

int getNumberOfDigits(int num)
{
    int count = 0;
    while (num != 0)
    {
        num /= 10;
        count++;
    }
    return count;
}

int isPara(int n)
{
    if (n < 10)
        return 0;
    int numberOfDigit = getNumberOfDigits(n);
    int n_revert = getRevert(n);
    for (int i = 0; i < numberOfDigit; i++)
    {
        if (n % 10 != n_revert % 10)
            return 0;
        n /= 10;
        n_revert /= 10;
    }
    return 1;
}

int deleteDigit4(int n, int pos)
{
    if (pos == 1)
        return n % 1000;
    if (pos == 2)
    {
        int temp = n % 100;
        return (n / 1000) * 100 + temp;
    }
    if (pos == 3)
    {
        int temp = n % 10;
        return (n / 100) * 10 + temp;
    }
    if (pos == 4)
    {
        return n / 10;
    }
}
int deleteDigit3(int n, int pos)
{
    if (pos == 1)
    {
        return n % 100;
    }
    if (pos == 2)
    {
        int temp = n % 10;
        return (n / 100) * 10 + temp;
    }
    if (pos == 3)
    {
        return n / 10;
    }
}

int maxPara(int n)
{
    int max = -1;
    if (isPara(n))
        return n;
    for (int i = 1; i <= 4; i++)
    {
        int temp = deleteDigit4(n, i);
        if (isPara(temp) && temp > max)
            max = temp;
    }

    for (int i = 1; i <= 4; i++)
    {
        int temp = deleteDigit4(n, i);
        for (int j = 1; j <= 3; j++)
        {
            int temp2 = deleteDigit3(temp, j);
            if (temp2 > max && isPara(temp2))
                max = temp2;
        }
    }

    return max;
}

int main()
{
    int n;
    cin >> n;

    cout << maxPara(n);
    return 0;
}