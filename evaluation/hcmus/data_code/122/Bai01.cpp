#include <iostream>
#include <cmath>
using namespace std;

void setArray (int Matrix[100][100], int n)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            cin >> Matrix[i][j];
        }
    }
}

int tinh_Tong_duongcheochinh (int Matrix[100][100], int n)
{
    int sum = 0;

    for (int i = 0; i < n; i++)
    {
        sum += Matrix[i][i];
    }

    return sum;
}

int tinh_Tong_duongcheophu (int Matrix[100][100], int n)
{
    int sum = 0;
    int temp = n - 1;

    for (int i = 0; i < n; i++)
    {
        sum += Matrix[i][temp];
        temp--;
    }

    return sum;
}

int tinh_Tong_matrix (int Matrix[100][100], int n)
{
    int sum = 0;
    
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            sum += Matrix[i][j];
        }
    }

    return sum;
}

int tinh_Tong_cacso_tren_duongcheophu (int Matrix[100][100], int n)
{
    int sum = 0;
    int temp = n - 1;

    for (int i = 0; i < n - 1; i++)
    {
        for (int j = 0; j < temp; j++)
        {
            sum += Matrix[i][j];
        }
        temp--;
    }

    return sum;
}

int tinh_Tong_cacso_tren_duongcheochinh (int Matrix[100][100], int n)
{
    int sum = 0;
    int temp = 0;

    for (int i = 0; i < n - 1; i++)
    {
        for (int j = n - 1; j > temp; j--)
        {
            sum += Matrix[i][j];
        }
        temp++;
    }

    return sum;
}

bool ktra_doixung_duongcheo_chinh (int Matrix[100][100], int n)
{
    int a = tinh_Tong_cacso_tren_duongcheochinh (Matrix, n);
    int b = tinh_Tong_matrix (Matrix, n);
    int c = tinh_Tong_duongcheochinh (Matrix, n);

    int d = (b - c) / 2;

    if (d == a) return true;
    return false;
}

bool ktra_doixung_duongcheo_phu (int Matrix[100][100], int n)
{
    int a = tinh_Tong_cacso_tren_duongcheophu (Matrix, n);
    int b = tinh_Tong_matrix (Matrix, n);
    int c = tinh_Tong_duongcheophu (Matrix, n);

    int d = (b - c) / 2;

    if (d == a) return true;
    return false;
}

int main ()
{
    int m = 0, n = 0;
    
    cin >> m;

    n = sqrt(m);

    int Matrix[100][100];
    setArray (Matrix, n);

    if (ktra_doixung_duongcheo_chinh (Matrix, n) == true) cout << "True";
    else if (ktra_doixung_duongcheo_phu (Matrix, n) == true) cout << "True";
    else cout << "False";

    return 0;
}