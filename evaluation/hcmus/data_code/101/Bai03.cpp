#include <iostream>
#include <cstring>
#define MAX 1000

using namespace std;

struct DoiTuyen
{
	char name[40];
	int like;
	int comment;
	int share;
};

void nhap(DoiTuyen& a)
{
	cout << "Nhap ten doi: ";
	cin.ignore();
	cin.getline(a.name, 40);
	cout << "Nhap so luot like: ";
	cin >> a.like;
	cout << "Nhap so luot comment: ";
	cin >> a.comment;
	cout << "Nhap so luot share: ";
	cin >> a.share;
}
void xuat(DoiTuyen a)
{
	cout << a.name << endl;
}
int tinhDiem(DoiTuyen a)
{
	return a.like + a.comment * 2 + a.share * 3;
}
void swap(DoiTuyen& a, DoiTuyen& b)
{
	DoiTuyen c;
	c = a;
	a = b;
	b = c;
}
void sapxepDoiTuyen(DoiTuyen a[], int size)
{
	for (int i = 0; i < size; i++)
	{
		int max_pos = i;
		for (int j = i + 1; j < size; j++)
		{
			if (tinhDiem(a[i]) < tinhDiem(a[j]))
				max_pos = j;
		}
		if (max_pos != i)
			swap(a[i], a[max_pos]);
	}
}
int main()
{
	int n;
	cout << "Nhap so luong nhom: ";
	cin >> n;
	DoiTuyen a[MAX];
	for (int i = 0; i < n; i++)
	{
		nhap(a[i]);
	}
	sapxepDoiTuyen(a, n);
	for (int i = 0; i < 3; i++)
	{
		xuat(a[i]);
	}
	return 0;
}