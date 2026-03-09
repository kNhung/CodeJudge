#include<iostream>
#include<cmath>
using namespace std;

void Nhap(int &n){
    cin >> n;
    while(n < 1000 || n > 9999){
        cin >> n;
    }
    return;
}

bool CheckDoiXung(int n){
    int Dem(0);
    while(n > 0){
        n /= 10;
        Dem++;
    }
    int pow10 = pow(10,(Dem - 1));
    //dem chan
    if(Dem % 2 == 0){
        for(int i = pow10; i < 0; i /= 10){
            for(int j = 10; j <= n; j *= 10){
                if( ((n - (n % i)) / pow10) != (n % j)) return false;
            }
        }
    }else{
        int pow10 = pow(10,((Dem - 1) / 2));
        for(int i = pow10; i < 0; i /= 10){
            for(int j = 10; j <= n; j *= 10){
                if((n % i) != (n % j)) return false;
            }
        }
    }
    return true;
}

int XoaMotSo(int n){
    int pow10 = 10;
    int DapSo(0);
    int SoDoiXung(0), SoDoiXungMax(0);
    while(pow10 / 10 <= n){
        int d = n % pow10;
        int right = d % (pow10/10);
        int left = n / pow10;
        DapSo = left*(pow10/10) + right;
        pow10 *= 10;
        if(CheckDoiXung(DapSo)){
            SoDoiXung = DapSo;
            if(SoDoiXung >= SoDoiXungMax){
                SoDoiXungMax = SoDoiXung;
            }
        }
    }
    if(SoDoiXungMax != 0) return SoDoiXungMax;
    else return -1;
}

int main(){
    int n(0);
    Nhap(n);
    //cout << n;
    cout << XoaMotSo(n);
    return 0;
}