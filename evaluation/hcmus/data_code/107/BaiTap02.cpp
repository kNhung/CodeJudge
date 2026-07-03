//23127077
#include <iostream>
#include <cstring>
#include <cmath>

const int MAX = 100;

using namespace std;

void xoaChuTrung(char s[]);
void xoaChu(char s[], int x);
int returnLength(char s[]);

int main()
{
	char s[100];
	cin.getline(s, 100);
	xoaChuTrung(s);
	return 0;
}

void xoaChuTrung(char s[])
{
	int len = strlen(s);
	for (int i = 0; i < len; i++)
	{
		if (s[i] == s[i + 1])
		{
			xoaChu(s, i);
			xoaChu(s, i);
			i = -1;
			len -= 2;
		}	
	}
	
	len = strlen(s);
	for (int i = 0; i < len; i++)
	{
		cout << s[i];
	}
	
	return;
}

void xoaChu(char s[], int x)
{
	int len = strlen(s);
	for (int i = x; i < len; i++)
	{
		s[i] = s[i + 1];
	}
	
	return;
}
