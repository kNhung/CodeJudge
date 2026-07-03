// Đề bài: Một số automorphic là một số tự nhiên mà bình phương của nó chứa số kết thúc bằng chính nó. Viết chương trình nhập vào một số nguyên dương n (n > 0), kiểm tra n có phải là số automorphic hay không. 
// In ra 1 nếu n là số automorphic, ngược lại, in ra 0.

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
bool Automorphic(int n){
	int tmp = n * n;
	int mov = pow(10, DemChuSo(n));
	int num = tmp % mov;
	
	if (num == n)
		return true;
	return false;
}

int main(){
    int n;
    cin >> n;

    cout << Automorphic(n) << endl;
    return 0;
}