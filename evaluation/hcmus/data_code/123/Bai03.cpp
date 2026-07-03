#include<iostream>
#include<cstring>
using namespace std;
#define MAX 100
struct doituyen {
    char name[40];
    int like;
    int comment;
    int share;
    float diem;
};
void NHAP(doituyen a[], int& n){
    cout << "Nhap n: ";
    cin >> n;
    //char k[] = "000";
    for(int i = 0; i <n; i++){
        
   
        cout << "Nhap name: ";
        cin.ignore();
        cin.getline(a[i].name, MAX);
        cout << "Nhap so luot like: ";
        cin >> a[i].like;
        cout << "Nhap so luot comment: ";
        cin >> a[i].comment;
        cout << "Nhap so luot share: ";
        cin >> a[i].share;
        cout << endl;
        

    }
        //while(strcmp(a.name, k) == 0);
        
    }

float TINHDIEM(doituyen x){
     x.diem = x.like * 1 + x.comment * 2 + x.share * 3;
    return x.diem;
}
/*void VITHU(int n){
    //doituyen a[MAX];
    int v1 = 1;
    int v2 = 2;
    int v3 = 3;


    for(int i = 0; i < n; i++){
        if()

    }
    
}*/

void XUAT(doituyen a[], int n){
    char LON1[MAX];
    char LON2[MAX];
    char LON3[MAX];
    for(int i = 0; i < n; i++){
        int k = TINHDIEM(a[i]);
        int max1 = INT_MAX;
        int max2 = INT_MAX;
        int max3 = INT_MAX;
        if(a[i].diem > max1){
            max1 = a[i].diem;
            strcmp(LON2, a[i].name);

        }
        else if(a[i].diem > max2  ){
        max2 = a[i].diem;
        strcmp(LON2, a[i].name);

        }
        else if(a[i].diem > max3){
            max3 = a[i].diem;
            strcmp(LON3, a[i].name);

        }
        cout << a[i].name << "\t" << a[i].like << "\t" << a[i].comment << "\t" << a[i].share << "\t " << k << endl;

    }
}

int main(){
    doituyen a[MAX];
    int n;

    NHAP(a, n);
    XUAT(a, n);
}

