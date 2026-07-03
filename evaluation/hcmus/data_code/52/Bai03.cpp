// Đề bài: Số nguyên n gọi là số đối xứng là số có từ 2 chữ số trở lên và nếu đọc từ trái qua phải, hay từ phải qua trái đều được số giống nhau. Viết chương trình nhập vào một số nguyên dương n (1000 <= n <= 9999), in ra số đối xứng lớn nhất có thể tạo ra được bằng việc xóa con số bất kì trong n.
// Lưu ý: số lượng con số bị xóa chưa được xác định.

#include <iostream>

using namespace std;

int DemChuSo(int n){
	int cnt = 0;
	while (n > 0){
		n /= 10;
		cnt++;
	}
	return cnt;
}

bool DoiXung(int n){
    int no = n;
    int ndn = 0;
    while (no != 0){
        ndn = ndn * 10 + (no % 10);
        no = no / 10;
    }
    if (ndn == n)
        return true;
    else
        return false;
}

int XoaChuSo(int n, int i){
    int res = 0;
    if (i == 1)
        res = n % 1000;
    else if (i == 2)
        res = ((n / 1000) * 100) + n % 100;
    else if (i == 3)
        res = ((n / 100) * 10) + n % 10;
    else if (i == 4)
        res = n / 10;
    return res;
}

int SoDaoNguocLonNhat(int n){
    if (DemChuSo(n) < 2)
        return -1;
    if (DoiXung(n) == 1)
        return n;
    int res = 0;
    for (int i = 1; i <= 4; i++){
        int temp = XoaChuSo(n, i);
        if (DoiXung(temp) == 1 && res < temp)
            res = temp;
    }
    if (res != 0)
        return res;
    for (int i = 1; i <= 3; i++)
        for (int j = i + 1; j <= 4; j++){
            int temp = XoaChuSo(n, j);
            temp = XoaChuSo(n, i);
            if (DoiXung(temp) == 1 && res < temp)
            res = temp;
        }
    if (res != 0)
        return res;
    while (n != 0){
        int temp = n % 10;
        if (DoiXung(temp) == 1 && res < temp)
            res = temp;
        n = n / 10;
    }
    return res;
}   

int main(){
    int n;
    cin >> n;
    cout << SoDaoNguocLonNhat(n) << endl;
    return 0;
}