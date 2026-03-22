#include <iostream>
#include <cmath>
#include<string>
#include<cstring>
#include <cstdlib>
#include <stdlib.h>
#include <fstream>
#define Max 100

using namespace std;
struct pokemon
{
    char id[50];
    char name[50];
    char type1[50];
    char type2[50];
    int speed;

};
/*void Printpoke(int i)
    {
        cout<<x[i].id;
        cout<< x[i].name;
        cout<<x[i].type1;
        cout<<x[i].type2;
        cout<<x[i].speed;
    }*/
int main()
{
    pokemon x[Max];
    ifstream file;
    file.open("pokemon.txt");
    int n=3;

    cout<<n;
    for(int i=0;i<n;i++)
    {
        file>>x[i].id;
        file >> x[i].name;
        file >>x[i].type1;
        file >>x[i].type2;
        file>>x[i].speed;
    }
    int max=0;int vitri=0;
    for(int i=0;i<n;i++)
    {
        if(x[i].speed>max){
            max=x[i].speed;
            vitri=i;
        }
    }
    //Printpoke(vitri);
    for(int i=0;i<n;i++)
    {
        if(x[i].speed==max){
        cout<<x[i].id;
        cout<< x[i].name;
        cout<<x[i].type1;
        cout<<x[i].type2;
        cout<<x[i].speed;

        }
    }
    file.close();
    return 0;
}
