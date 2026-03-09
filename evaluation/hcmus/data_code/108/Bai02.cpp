#include <iostream>
#include <cstring>

using namespace std;

const int MAX = 1000;

void solve(char a[]){
	int i = 0;
	int len = strlen(a);
	while (a[i] != 0){
		if (a[i] == a[i + 1]){
			a[i - 1] = a[i + 1];
			len = len - 2;
			i = 0;
		}
		else{
			i++;
		}
	}
	
	a[len] = 0;
}

int main(){
	char a[MAX];
	cin.getline(a, 1000);
	solve(a);
	cout << 1;
	
	return 0;
	
	
}
