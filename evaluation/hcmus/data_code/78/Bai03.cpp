#include <iostream>

using namespace std;

bool isInt(float a){
    if (static_cast<int>(a) != a){
        return false;
    }
    else{
        return true;
    }
}

int pow10(int n){
    int pow(1);

    for (int i = 1; i <= n; i++){
        pow *= 10;
    }

    return pow;
}

int demsoChuSo(int n){
    int count(0);

    while (n != 0){
        n /= 10;
        count++;
    }

    return count;
}

int daonguocSo(int n){
    int count = demsoChuSo(n);
    int m, num(0);

    for (int i = count; i > 0; i--){
        m = n % 10;
        n /= 10;

        num += m * pow10(i - 1);
    }

    return num;
}

int demTanSuatXuatHien(int n){
    int m, count = demsoChuSo(n);
    int count1(0), count2(0), count3(0), count4(0), count5(0);
    int count6(0), count7(0), count8(0), count9(0);

    for (int i = 1; i <= count; i++){
        m = n % 10;
        n /= 10;

        switch (m){
            case 1:
                count1++;

                if (count1 >= 2){
                    return 1;
                }

                break;
            case 2:
                count2++;

                if (count2 >= 2){
                    return 2;
                }

                break;
            case 3:
                count3++;

                if (count3 >= 2){
                    return 3;
                }

                break;
            case 4:
                count4++;

                if (count4 >= 2){
                    return 4;
                }

                break;
            case 5:
                count5++;

                if (count5 >= 2){
                    return 5;
                }

                break;
            case 6:
                count6++;

                if (count6 >= 2){
                    return 6;
                }

                break;
            case 7:
                count7++;

                if (count7 >= 2){
                    return 7;
                }

                break;
            case 8:
                count8++;

                if (count8 >= 2){
                    return 8;
                }

                break;
            default:
                count9++;

                if (count9 >= 2){
                    return 9;
                }
        }

    }

    return 0;
}

int timMin_xoaMin(int n, int execpt){
    int Min(100), count(0), count_Min, m;
    int n_temp = n;

    while (n_temp != 0){
        m = n_temp % 10;
        n /= 10;

        count++;

        if (m < Min && m != execpt){
            Min = m;

            count_Min = count;
        }
        else{
            continue;
        }
    }

    int d = n % pow10(count_Min);
    int right = d % (pow10(count_Min) / 10);
    int left = n / pow10(count_Min);
    int num = left*(pow10(count_Min) / 10) + right;

    return num;
}

int main(){
    float n_fl;

    cout << "Nhap n ( 1000 <= n <= 9999): ";
    cin >> n_fl;

    if (n_fl < 1000 || n_fl > 9999){
        cout << "Wrong input";

        return 0;
    }

    if (isInt(n_fl) == false){
        cout << "Hay nhap vao so nguyen";

        return 0;
    }

    int n = int(n_fl);
    int n_temp = n;

    if (demTanSuatXuatHien(n) == 0){
        cout << "-1";
        return 0;
    }

    //TH: n = abab (2323 || 3232)
    if (daonguocSo(n) - n == 909){
        int m = daonguocSo(n);

        m /= 10;
         
        cout << m;
        return 0;
    }
    else if (daonguocSo(n) - n == -909){
        int m = n / 10;

        cout << m;
        return 0;
    }
    else{
        while (daonguocSo(n) != n){
            n_temp = timMin_xoaMin(n, demTanSuatXuatHien(n));
        }

        n = n_temp;

        cout << n;

        return 0;
    }


    return 0;
}