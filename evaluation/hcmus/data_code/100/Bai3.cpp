#include <iostream>
#include <cstring>
#include <cmath>

using namespace std;

#define MAX 100

struct DoiTuyen{
    char Name[40];
    int Like;
    int Comment;
    int Share;
};

int TinhDiem(DoiTuyen DT){
    return DT.Like * 1 + DT.Comment * 2 + DT.Share * 3;
}

int SoSanh(DoiTuyen DT1, DoiTuyen DT2){
    if (TinhDiem(DT1) > TinhDiem(DT2))
        return 1;
    if (TinhDiem(DT1) < TinhDiem(DT2))
        return 2;
    if (DT1.Share > DT2.Share)
        return 1;
    if (DT1.Share < DT2.Share)
        return 2;
    if (DT1.Comment > DT2.Comment)
        return 1;
    if (DT1.Comment < DT2.Comment)
        return 2;
    if (DT1.Like > DT2.Like)
        return 1;
    if (DT1.Like < DT2.Like)
        return 2;
    return 0;
}

int main(){
    DoiTuyen DTs[MAX];
    int n = -1;
    int res[MAX];
    int Max1 = 0, Max2 = 0, Max3 = 0;
    while (true){
        char temp[40];
        cout << "Name: ";
        cin.ignore();
        cin.getline(temp, 40);
        if (strcmp(temp, "000") == 0)
            break;
        n++;
        strcpy(DTs[n].Name, temp);
        cout << "Like: ";
        cin >> DTs[n].Like;
        cout << "Comment: ";
        cin >> DTs[n].Comment;
        cout << "Share: ";
        cin >> DTs[n].Share;
        if (SoSanh(DTs[n], DTs[Max1]) == 1){
            Max3 = Max2;
            Max2 = Max1;
            Max1 = n;
        }
        else if (SoSanh(DTs[n], DTs[Max2]) == 1){
            Max3 = Max2;
            Max2 = n;
        }
        else if (SoSanh(DTs[n], DTs[Max3]) == 1)
            Max3 = n;
        cout << endl;
    }
    cout << DTs[Max1].Name << endl;
    cout << DTs[Max2].Name << endl;
    cout << DTs[Max3].Name << endl;
    // for (int i = 0; i < n - 1; i++)
    //     for (int j = i + 1; j < n; j++)
    //         if ()
    return 0;
}