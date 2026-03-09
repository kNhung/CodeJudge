#include <iostream>
#include <string.h>
#include <cmath>
using namespace std;
#define MAX 100
struct OL {
    char name[40];
    int like ;
    int cmt;
    int share;
    int soccer = like*1+cmt*2+share*3;
    void output();
    
};
void OL::output(){

        cout<<"NAME:"<<name<<endl;
        cout<<"Like:"<<like<<endl;
        cout<<"Comment:"<<cmt<<endl;
        cout<<"Share:"<<share<<endl;
       
}
void input(OL a[MAX],int n){
       
    for(int i = 0;i<n;i++){
        cin.ignore();
        cout<<"NAME:";
        cin.getline(a[i].name,40);
        cout<<"Like:";
        cin>>a[i].like;
        cout<<"Comment:";
        cin>>a[i].cmt;
        cout<<"Share:";
        cin>>a[i].share;
        cout<<endl;
    }
}

void Sort_Team(OL a[MAX],int n ){
    for(int i = 0 ; i < n ; i ++){
        int tempi = a[i].like*1+a[i].cmt*2+a[i].share*3;
        for(int j = 0;j<n;j++ ){
            int tempj = a[j].like*1+a[j].cmt*2+a[j].share*3;
            if(a[i].soccer <= a[j].soccer){
                if(a[i].soccer < a[j].soccer){
                    int tmp = a[i].soccer;
                    a[i].soccer=a[j].soccer;
                    a[j].soccer=tmp;
                }
                else { // tempi == tempj 
                    if(a[i].share<=a[j].share){
                        if(a[i].share < a[j].share){
                            int tmp1 = a[i].share;
                            a[i].share=a[j].share;
                            a[j].share=tmp1;
                        }
                        else { // share = share
                            if(a[i].cmt <= a[j].cmt){
                                if(a[i].cmt < a[j].cmt){
                                    int tmp2 = a[i].cmt;
                                    a[i].cmt=a[j].cmt;
                                    a[j].cmt=tmp2;
                                }
                                else {//cmt = cmt;
                                    if(a[i].like < a[j].like){
                                        int tmp3 = a[i].like;
                                        a[i].like=a[j].like;
                                        a[j].like=tmp3;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
            if(n <= 2 ){
                for(int i = 0; i < n ; i ++){
                    a[i].output();
                }
            }
            else 
               a[0].output();
               cout<<endl;
               a[1].output();
               cout<<endl;
               a[2].output();

}

int main (){
    OL a[MAX];
    int n ;
    cout<<"Nhap so luong doi:";
    cin>>n;
    cout<<"Nhap danh sach doi:"<<endl;
    
    input(a,n);
    cout<<endl;
    Sort_Team(a,n);

    return 0;

}

