#include<iostream>

using namespace std;

#define MAX 50

struct thongtin
{
    char name[40];
    int like;
    int comment;
    int share;

    void inp();
};

void thongtin::inp()
{
    cin.get(name,40);
    cin >> like;
    cin >> comment;
    cin >> share;
}

int tinhDiem(thongtin a)
{
    int tongdiem = a.like + a.comment*2 + a.comment*3;

    return tongdiem;
}

int main()
{
    thongtin doi[MAX];
    int n = 0;
    while(doi[n].name == "000")
    {
        doi[n].inp();
        n++;
    }
    
    int b[20];

    for(int j = 0; j < n; j++)
    {
        int diem = tinhDiem(doi[j]);
        b[j] = diem;
    }

    int c[20];
    int h = 0;

    int i, j, min_idx;

	for (i = 0; i < n - 1; i++) 
    {
		min_idx = i;

		for (j = i + 1; j < n; j++) 
        {
			if (b[j] < b[min_idx])
				min_idx = j;
		}

		if (min_idx != i)
        {
            int temp = b[min_idx];
            b[min_idx] = b[i];
            b[i] = temp;
        }

        c[h++] = min_idx;
	}

    doi[c[0]].name;
    doi[c[1]].name;
    doi[c[2]].name;

    return 0;
    
}