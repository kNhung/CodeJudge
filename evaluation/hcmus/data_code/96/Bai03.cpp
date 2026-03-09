#include <iostream>
#include <cstring>
#include <cmath>

using namespace std;

#define MAX 1000

struct DoiTuyen
{
    char name[41];
    int like;
    int cmt;
    int share;
};

int sumMark(DoiTuyen dt)
{
    int sum = 0;
    sum = sum + dt.like + dt.cmt * 2 + dt.share * 3;
    return sum;
}

void swap(DoiTuyen &a, DoiTuyen &b)
{
    DoiTuyen temp = a;
    a = b;
    b = temp;
}

void sortArray(DoiTuyen dt[], int n)
{
    int max = 0;
    int sum = 0;
    for (int i = 0; i < n; i++)
    {
        int temp1 = sumMark(dt[i]);
        for (int j = i; j < n; j++)
        {
            int temp2 = sumMark(dt[j]);
            if (temp1 < temp2)
            {
                swap(dt[i], dt[j]);
            }
        }
    }
}

void sortEqual(DoiTuyen dt[], int n, int &f)
{
    int count = 0;
    for (int i = 0; i < n; i++)
    {
        if (sumMark(dt[i]) > sumMark(dt[i + 1]))
            count++;
        if (sumMark(dt[i]) == sumMark(dt[i + 1]))
        {
            int check1 = 0, check2 = 0;
            for (int j = 0; j < 3; j++)
            {
                if (dt[i].like > dt[i + 1].like)
                    check1++;
                else if (dt[i].like < dt[i + 1].like)
                    check2++;

                if (dt[i].cmt > dt[i + 1].cmt)
                    check1++;
                else if (dt[i].cmt < dt[i + 1].cmt)
                    check2++;

                if (dt[i].share > dt[i + 1].share)
                    check1++;
                else if (dt[i].share < dt[i + 1].share)
                    check2++;
            }
            if (check1 > check2)
                count++;
            if (check1 < check2)
            {
                swap(dt[i], dt[i + 1]);
                count++;
            }
        }
        if (count == 3)
        {
            f = i;
            break;
        }
    }
}

int main()
{
    DoiTuyen dt[MAX];
    int n, i = 0;
    char temp[MAX];

    while (true)
    {
        cout << "Name: ";
        cin.getline(temp, MAX);
        if (strcmp(temp, "000") == 0)
            break;
        strcpy(dt[i].name, temp);
        cout << "Like: ";
        cin >> dt[i].like;
        cout << "Comment: ";
        cin >> dt[i].cmt;
        cout << "Share: ";
        cin >> dt[i].share;

        cout << endl;

        cin.ignore();
        i++;
    }

    sortArray(dt, i);
    cout << endl
         << endl;

    int temp1 = 0;
    sortEqual(dt, i, temp1);

    if (temp1 != 0)
        for (int i = 0; i < temp1; i++)
            cout << dt[i].name << endl;
    else
        for (int i = 0; i < 3; i++)
            cout << dt[i].name << endl;

    return 0;
}