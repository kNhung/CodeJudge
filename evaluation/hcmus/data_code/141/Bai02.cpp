// Cho chuỗi kí tự s gồm các chữ cái tiếng anh viết thường. Thực hiện xóa các chữ cái trùng nhau
// nằm liên tiếp nhau trong chuỗi. Sau khi xóa nếu chuỗi mới vẫn tồn tại các chữ cái nằm kề nhau
// trùng nhau thì tiếp tục thực hiện việc xóa. Lưu ý, việc xoá diễn ra từ trái sang phải. Viết hàm
// thay đổi chuỗi s sau khi thực hiện việc xóa các kí tự trùng lặp trong chuỗi và in ra chuỗi s đó.
// VD:
// Input:
// abbaca
// Output:
// ca
// Giải thích: abbaca => xóa bb => aaca => xóa aa => ca
#include <iostream>
#include <string.h>
#include <cmath>
using namespace std;
#include <iostream>
#include <string>
using namespace std;

string removeDuplicates(string s) {
    string result;
    for (char c : s) {
        if (!result.empty() && result.back() == c) {
            result.pop_back();
        } else {
            result.push_back(c);
        }
    }
    return result;
}

int main() {
    string s = "abbaca";
    string result = removeDuplicates(s);
    cout << result << endl;
    return 0;
}
