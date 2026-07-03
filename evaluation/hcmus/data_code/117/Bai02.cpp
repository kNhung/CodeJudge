#include <iostream>
#include <cstring>

using namespace std;

void deleteElement (char c[], int &n, int start, int end) {
    int dis = end - start + 1;
    for (int i = start; i <= end; i++) {
        c[i] = c[i + dis];
    }
    n -= dis;
    c[n] = '\0';
}

void deleteChar(char c[]){
    int n = strlen(c);
    for (int i = 0; i < n; i++) {
            int j = i ;
            bool flag = false;
            while (c[j] == c[j + 1]) {
                j++;
                flag = true;
            }
            if (flag == true) {
                deleteElement(c, n, i, j);
                i = -1;
            }
    }
}

int main() {
    char c[100];
    cin >> c;
    deleteChar(c);
    cout << c;
    return 0;
}