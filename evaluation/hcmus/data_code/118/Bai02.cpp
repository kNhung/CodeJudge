#include<iostream>
#include<cstring>
#define MAX 50
using namespace std;


void In(char a[], int n){
    for(int i = 0; i < n; ++i){
        cout << a[i];
    }
}



void Delete(char a[], int &n, int start, int end){
    int tmp1 = 0;
    for(int i = start; i <= n - 1; ++i){
        int tmp = a[end + tmp1 + 1];
        tmp1++;
        a[i] = a[start + end ];
        a[i + 1] = tmp;
    }
    n -= (end - start + 1);
}

bool ktraTrung(char a[], int start, int end, int n){
    bool check = false;
    for(int i = 0; i < n; ++i){
        if(a[i] == a[i + 1]){
            start = i;
            check = true;
        }

        if(a[i] != a[i + 1] && check == true){
            end = i; 
            return true;
        }
    }
    return false;
}

void XoaLientuc(char a[], int &start, int &end, int &n){
    while(ktraTrung(a,start,end,n)){
        Delete(a,start, end,n);
    }
}

int main(){
    char a[50];
    cin >> a;
    int start, end;
    int n = strlen(a);
    Delete(a,n,1,2);
    In(a,n);
    return 0;
}