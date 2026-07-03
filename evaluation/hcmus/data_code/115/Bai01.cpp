#include <iostream>
#include <cmath>
#define MAX 100
using namespace std;
void nhap_ma_tran(int a[][MAX], int n)
{
	for(int i = 0; i < n; i++)
		for(int j = 0; j < n; j++)
			cin >> a[i][j];
}
void hoan_doi(int &a, int &b)
{
	int temp = a;
	a=b;
	b=temp;
}
bool kiemtra_doixung(int a[][MAX], int n)
{
	//duong cheo phu
	bool check1 = true;
	for(int i = 0; i < n; i++)
		for(int j = 0; j < n; j++)
			if( (a[i][j] != a[j][i]) ) 
				check1 = false;
	//doi xung mang qua chieu doc
	for(int i = 0; i < n; i++)
		for(int j = 0; j < n/2; j++)
			hoan_doi(a[i][j],a[i][n-1-j]);
	//duong cheo chinh
	bool check2 = true;
	for(int i = 0; i < n; i++)
		for(int j = 0; j < n; j++)
			if( (a[i][j] != a[j][i]) ) 
				check2 = false;
	//xu li
	if(check1 == true || check2 == true) return true;
	else return false;
}
int main()
{
	int a[MAX][MAX];
	int n;
	cout << "input: ";
	cin >> n; 
	int m = sqrt(n);
	nhap_ma_tran(a,m);
	if(kiemtra_doixung(a,m)) cout << "true";
	else cout << "false";
	return 0;
}
