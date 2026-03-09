#include<iostream>

using namespace std;

void xoaChuTrung(string s){
	int n=s.length();
	for(int i=0;i<n;i++){
		if(s[i]==s[i+1]){
			s[i]=s[i+2];
			s[i+1]=s[i+3];
			n-=2;
		}
	}
	for(int j=0;j<n;j++){
		cout<<s[j];
	}
}
int main(){
	string s;
	cout << "Nhap chuoi:";
	getline(cin, s);
	xoaChuTrung(s);
	return 0;
}
