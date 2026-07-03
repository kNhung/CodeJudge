#include <iostream>
#include <cstring>
using namespace std;

void del_char(char a[], int index)
{
	int n = strlen(a);
	for (int i = index; i < n - 1; i++)
	{
		a[i] = a[i + 1];
	}
	a[n] = '\0';
}

void del_denkhidung(char a[])
{
	int n = strlen(a);
	int count(0);
	while (a[count] != '\0')
	{
		if (a[count] = a[count + 1])
		{
			char tmp = a[count];
			while (a[count] == tmp)
			{
				del_char(a, count);
			}
			count = 0;
		}
	}
}

int main()
{
	char a[100];
	cin >> a;
	del_denkhidung(a);
	cout << a;
	return 0;
}