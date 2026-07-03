#include <iostream>
#include <cstring>
#define MAX 100 

using namespace std;

void inputArr(char s[]) {
	cout << "Input: ";
	cin.getline(s,MAX);
}

void deleteAt(char s[]) {
	int pos;
	int len = strlen(s);
	for(int i = pos; i < len; i++) {
		s[i] = s[i + 1];
	}
}

void timGiongNhau(char s[]) {
	
}

int main() {
	char s[MAX];
	inputArr(s);
	
	return 0;
}