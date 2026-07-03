#include <iostream>
#include <cstring>

using namespace std;

struct SinhVien
{
    char name[40];
    int like;
    int cmt;
    int shr;
    int tong;

    void input();
    void output();
};

void sapxep(SinhVien a[], int n)
{
    int max_pos = 100000;

    for (int i = 0; i < n; i++)
    {
        max_pos = i;
        for (int j = 0; j < n; j++)
            if (a[j].tong < a[max_pos].tong)
            {
                max_pos = i;
            }
        int tmp = a[max_pos].tong;
        a[max_pos].tong = a[i].tong;
        a[i].tong = tmp;

    } 
}

void SinhVien::input()
{
    cout <<"Name: ";
    cin >>name;
    cout <<"Like: ";
    cin >>like;
    cout <<"Comment: ";
    cin >>cmt;
    cout <<"Share: ";
    cin >>shr;
}

void SinhVien::output()
{
    cout <<name;
}

void nhapThongTin(SinhVien a[], int &n)
{
    cout <<"Nhap so doi tham gia: ";
    cin >>n;

    for (int i = 0; i < n; i++)
    {
        a[i].input();
        cout <<endl;
        if (a[i].name == "000")
            break;
    }
        
}

void tinhDiem(SinhVien a[], int n)
{
    for (int i = 0; i < n; i++)
        a[i].tong = (a[i].like * 1) + (a[i].cmt * 2) + (a[i].shr * 3);
}

void xuatTenBaDoiCaoNhat(SinhVien a[], int n)
{
    sapxep(a, n);
    for (int i = 0; i < 3; i++)
    {
        a[i].output();
        cout <<endl;
    }
        
}

int main()
{
    SinhVien a[100];
    int n;

    nhapThongTin(a, n);
    xuatTenBaDoiCaoNhat(a, n);


}