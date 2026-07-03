#include <iostream>
#include <cstring>
using namespace std;

struct club
{
	char name[41];
	int like;
	int  comment;
	int share;
	int point;
	void getDataclub();
};

void club::getDataclub()
{
	char tmp[100], c_like[100], c_comment[100], c_share[100];
	//lay ten doi
	cin.getline(tmp, 100);
	int n = strlen(tmp), space;
	for (int i = 0; i < n; i++)
	{
		if (tmp[i] == ' ')
		{
			space = i;
			break;
		}
	}
	int count(0);
	for (int i = space + 1; i < n; i++)
	{
		name[count] = tmp[i];
		count++;
	}
	name[count] = '\0';
	//tinh so like
	cin.getline(tmp, 100);
	n = strlen(tmp), space;
	for (int i = 0; i < n; i++)
	{
		if (tmp[i] == ' ')
		{
			space = i;
			break;
		}
	}
	count = 0;
	for (int i = space; i < n; i++)
	{
		c_like[count] = tmp[i];
		count++;
	}
	c_like[count] = '\0';
	like = atoi(c_like);
	// tinh so comment
	cin.getline(tmp, 100);
	n = strlen(tmp), space;
	for (int i = 0; i < n; i++)
	{
		if (tmp[i] == ' ')
		{
			space = i;
			break;
		}
	}
	count = 0;
	for (int i = space; i < n; i++)
	{
		c_comment[count] = tmp[i];
		count++;
	}
	c_comment[count] = '\0';
	comment = atoi(c_comment);
	//tinh so share
	cin.getline(tmp, 100);
	n = strlen(tmp), space;
	for (int i = 0; i < n; i++)
	{
		if (tmp[i] == ' ')
		{
			space = i;
			break;
		}
	}
	count = 0;
	for (int i = space; i < n; i++)
	{
		c_share[count] = tmp[i];
		count++;
	}
	c_share[count] = '\0';
	share = atoi(c_share);
}

void cal_pointclubs(club a[], int n)
{
	for (int i = 0; i < n; i++)
	{
		a[i].point = a[i].like + 2 * a[i].comment + 3 * a[i].share;
	}
}

void print_club(club a[], int n)
{
	club max = a[0];
	for (int i = 0; i < n; i++)
	{
		if (a[i].point > max.point)
		{
			max = a[i];
		}
		else if (a[i].point == max.point)
		{
			if (a[i].share > max.like)
			{
				max = a[i];
				continue;
			}
			if (a[i].comment > max.comment)
			{
				max = a[i];
				continue;
			}
			if (a[i].like > max.like)
			{
				max = a[i];
				continue;
			}
			if (a[i].share == max.like && a[i].comment == max.comment && a[i].like == max.like)
			{
				cout << a[i].name << " ";
			}
		}
	}
	cout << max.name << " ";
	club second;
	second.point = 0;
	for (int i = 0; i < n; i++)
	{
		if (a[i].name != max.name)
		{
			if (a[i].point > second.point)
			{
				second = a[i];
			}
			else if (a[i].point == second.point)
			{
				if (a[i].share > second.like)
				{
					second = a[i];
					continue;
				}
				if (a[i].comment > second.comment)
				{
					second = a[i];
					continue;
				}
				if (a[i].like > second.like)
				{
					second = a[i];
					continue;
				}
				if (a[i].share == second.like && a[i].comment == second.comment && a[i].like == second.like)
				{
					cout << a[i].name << " ";
				}
			}
		}
	}
	cout << second.name << " ";
	club third;
	third.point = 0;
	for (int i = 0; i < n; i++)
	{
		if (a[i].name != max.name && a[i].name != second.name)
		{
			if (a[i].point > third.point)
			{
				third = a[i];
			}
			else if (a[i].point == third.point)
			{
				if (a[i].share > third.like)
				{
					third = a[i];
					continue;
				}
				if (a[i].comment > third.comment)
				{
					third = a[i];
					continue;
				}
				if (a[i].like > third.like)
				{
					third = a[i];
					continue;
				}
				if (a[i].share == third.like && a[i].comment == third.comment && a[i].like == third.like)
				{
					cout << a[i].name << " ";
				}
			}
		}
		cout << third.name;
	}
}

int main()
{
	club a[100];
	a[0].getDataclub();
	int count(1);
	while (a[count].name != "000")
	{
		a[count].getDataclub();
		count++;
	}
	count++;
	cal_pointclubs(a, count);
	print_club(a, count);
	return 0;
}