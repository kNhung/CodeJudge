#include <iostream>
#include <cstring>

using namespace std;

void deletesame(char a[], int& length){
    int dem = 1;
    for(int i = 0; i < length; i++){
        if(a[i] == a[i + 1]){
            dem++;
            for(int k = i; k < length; k++)
                a[k] = a[k + 1];
        }
    }

    length -= dem;

    for(int j = 0; j < length; j++)
        cout << a[j];
}

int main(){
    char a[1000];
    cout << "Nhap chuoi ky tu: ";
    cin.getline(a, 1000);

    int length = strlen(a);

    deletesame(a, length);
}