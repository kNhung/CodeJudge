#include <iostream>
#include <cstring>

using namespace std;

struct DoiTuyen
{
    char Name[100];
    int Like;
    int Comment;
    int Share;
};

DoiTuyen InputDoiTuyen ()
{
    DoiTuyen a;
    cin.ignore();
    cout << "Name: ";
    cin.getline (a.Name, 100);
    cout << "Like: ";
    cin >> a.Like;
    cout << "Comment: ";
    cin >> a.Comment;
    cout << "Share: ";
    cin >> a.Share;

    return a;
}

void tinhDiem (int DiemSo[], int n, DoiTuyen CacDoiThamGia[])
{
    int ketqua = 0;

    for (int i = 0; i < n; i++)
    {
        DiemSo[i] = CacDoiThamGia[i].Like + (CacDoiThamGia[i].Comment * 2) + (CacDoiThamGia[i].Share * 3);
    }
}

int tim_vi_tri_doi_cao_nhat (int DiemSo[], int n)
{
    int max = DiemSo[0];
    int pos = 0;
    for (int i = 0; i < n; i++)
    {
        if (DiemSo[i] > max)
        {
            max = DiemSo[i];
            pos = i;
        }
    }

    return pos;
}

int main ()
{
    int n = 0;
    DoiTuyen CacDoiThamGia [1000];

    cout << "Nhap so doi tham gia: ";
    cin >> n;

    int DiemSo[n];

    for (int i = 0; i < n; i++)
    {
        CacDoiThamGia[i] = InputDoiTuyen ();
    }

    tinhDiem (DiemSo, n, CacDoiThamGia);

    int pos = tim_vi_tri_doi_cao_nhat (DiemSo, n);

    cout << CacDoiThamGia[pos].Name << endl;

    return 0;
}