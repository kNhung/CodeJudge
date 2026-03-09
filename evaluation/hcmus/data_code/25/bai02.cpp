#include <iostream>
using namespace std;

const int N = 1e3 + 25;

int n, m;
int a[N][N];
int res[N][N];

void solve(int a[][N], int n, int m) {
    for (int i = 1; i <= n; ++i) {
        int index = 1;
        for (int j = m; j >= 1; --j)
            res[i][index++] = a[i][j];
    }
}

void output(int a[][N], int n, int m) {
    for (int i = 1; i <= n; ++i) {
        for (int j = 1; j <= m; ++j)
            cout << a[i][j] << " ";
        cout << '\n';
    }
}

int main() {
    cout << "Input dim: ";
    cin >> n >> m;
    cout << "Input Arr: ";
    for (int i = 1; i <= n; ++i)
        for (int j = 1; j <= m; ++j)
            cin >> a[i][j];

    solve(a, n, m);

    cout << "Output: \n";
    output(res, n, m);
    return 0;
}

