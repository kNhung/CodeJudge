#include <iostream>
#include <cstring>
#define MAX 100
using namespace std;
struct Team
{
	char name[MAX];	
	int like;
	int cmt;
	int share;
	void input();
	void print();
	int diem;
};
void Team::input()
{
	cout << "name: ";
	cin.getline(name,MAX);
	cout << "like: ";
	cin >> like;
	cout << "comment: ";
	cin >> cmt;
	cout << "share: ";
	cin >> share;
	cin.ignore();
}
void Team::print()
{
	cout << name << endl;
}
void nhap_mang(Team A[], int &n)
{
	n = 0;
	char temp[MAX] = "000";
	A[n].input();
	//khi input 000 thi phai nhap them 0 0 0 
	while( strcmp(A[n].name, temp) != 0 )
	{
		n++;
		A[n].input();
		//if(strcmp(A[n].name, temp) == 0) break;
	}
}
void hoan_doi(Team &A, Team &B)
{
	Team tmp = A;
	A = B;
	B = tmp;
}
void tinh_diem(Team A[], int n)
{
	for(int i = 0; i < n; i++)
	{
		A[i].diem = A[i].like*1 + A[i].cmt*2 + A[i].share*3; 
		//a[m++] = A[i].diem; // m = n
	} 
	int max = 0; 
	for(int i = 0; i < n; i++)
	{
		for(int j = i + 1; j < n; j++)
		{
			if(A[i].diem < A[j].diem)
			{
				hoan_doi(A[i],A[j]);
			}
			else if(A[i].diem = A[j].diem)
			{
				if(A[i].share < A[j].share) 
					hoan_doi(A[i],A[j]);
				else if(A[i].share = A[j].share)
				{
					if(A[i].cmt < A[j].cmt) 
						hoan_doi(A[i],A[j]);
					else if(A[i].cmt = A[j].cmt)
					{
						if(A[i].like < A[j].like) 
							hoan_doi(A[i],A[j]);
					}
				}
			}
		}
	}
}
void xuat_mang(Team A[], int n)
{
	for(int i = 0; i < n; i++)
	{
		A[i].print();
	}
}
int main()
{
	Team A[MAX];
	int n;
	nhap_mang(A,n);
	tinh_diem(A,n);
	xuat_mang(A,n);
	return 0;
}
