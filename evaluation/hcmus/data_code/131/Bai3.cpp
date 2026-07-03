#include <iostream>
#include <cstring>
using namespace std;
struct DoiTuyen{
	string TenDoi;
	int like;
	int comment;
	int share;
};
int TinhDiem(int like, int comment, int share){
	int TongDiem = 0;
	TongDiem = like*1 + comment*2 + share*3;
	return TongDiem;
}

int main(){
	
}

