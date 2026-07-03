#include <iostream>
#include <cstring>
using namespace std;
struct doi{
    char name[40];
    int like;
    int comment;
    int share;
    void in(){
        cin >> name >> like >> comment >> share;
    }
    int diem(){
        int diemm = 0;
        diemm = like + comment*2 + share*3;
        return diemm;
    }
};
void timdoi(struct doi VN[], int n)
{
    int max = 0;
    int max1 = 0, max2 = 0;
    for (int i = 0; i < n; i++)
    {
        if (VN[max].diem() < VN[i].diem())
        {
            max = i;
        }
    }
    for (int i = 0; i < n; i++)
    {   
        if (i != max)
        {
        if ((VN[max1].diem() <= VN[i].diem()))
        max1 = i;
        }
    }
    for (int i = 0; i < n; i++)
    {   
        if (i != max)
        {
            if (i != max1)
            if ((VN[max2].diem() <= VN[i].diem()))
                 max2 = i;
        }
    }
    cout << VN[max].diem() << VN[max1].diem() << VN[max2].diem();
}
int main(){
    
    return 0;
}