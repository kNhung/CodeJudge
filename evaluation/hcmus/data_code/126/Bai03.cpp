#include<iostream>

using namespace std;

struct DoiTuyen{
	string name;
	int like;
	int comments;
	int share;
};
DoiTuyen DSDoiTuyen[i];
void nhap(){
	int i=0;
	do{
	cout<<"Nhap ten doi tuyen: ";
	getline(cin, DSDoiTuyen[i].name);
	cout<<"Nhap so luot like: ";
	cin>>DSDoiTuyen[i].like;
	cout<<"Nhap so luot comment: ";
	cin>>DSDoiTuyen[i].comments;
	cout<<"Nhap so luot share: ";
	cin>>DSDoiTuyen[i].share;
	i++;
	}while(DSDoiTuyen[i].name!=000);
}
int tinhDiem(int Diem){
	Diem=DSDoiTuyen[i].like*1+DSDoiTuyen[i].comments*2+DSDoiTuyen[i].share*3;
	return Diem;
}
int main(){
	nhap();
	return 0;
}


