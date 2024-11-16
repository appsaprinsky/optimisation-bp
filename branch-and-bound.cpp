#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
#include <fstream>
using namespace std;

struct Item {
    int weight;
    int value;
};

struct Node {
    int level;  
    int profit;
    int weight;
    float bound;
};

bool cmp(Item a, Item b) {
    double r1 = (double)a.value / a.weight;
    double r2 = (double)b.value / b.weight;
    return r1 > r2;
}

float bound(Node u, int n, int W, vector<Item>& items) {
    if (u.weight >= W)
        return 0;
    float profit_bound = u.profit;
    int j = u.level + 1;
    int totweight = u.weight;

    while ((j < n) && (totweight + items[j].weight <= W)) {
        totweight += items[j].weight;
        profit_bound += items[j].value;
        j++;
    }

    if (j < n)
        profit_bound += (W - totweight) * (float)items[j].value / items[j].weight;

    return profit_bound;
}

int knapsack(int W, vector<Item>& items) {
    sort(items.begin(), items.end(), cmp);
    queue<Node> Q;
    Node u, v;
    u.level = -1;
    u.profit = u.weight = 0;
    Q.push(u);
    int maxProfit = 0;

    while (!Q.empty()) {
        u = Q.front();
        Q.pop();

        if (u.level == -1) v.level = 0;
        if (u.level == (int)items.size() - 1)
            continue;

        v.level = u.level + 1;
        v.weight = u.weight + items[v.level].weight;
        v.profit = u.profit + items[v.level].value;
        if (v.weight <= W && v.profit > maxProfit)
            maxProfit = v.profit;
        v.bound = bound(v, items.size(), W, items);
        if (v.bound > maxProfit)
            Q.push(v);

        // consider not taking the item
        v.weight = u.weight;
        v.profit = u.profit;
        v.bound = bound(v, items.size(), W, items);
        if (v.bound > maxProfit)
            Q.push(v);
    }

    return maxProfit;
}

int main() {
    vector<Item> items;

    ifstream file("input_data.txt");
    if (file.is_open()) {
        int weight, value;
        while (file >> weight >> value) {
            items.push_back({weight, value});
        }
        file.close();
    } else {
        cerr << "Unable to open file " << endl;
    }

    int W;
    ifstream file1("input_max_cap.txt");
    if (file1.is_open()) {
        file1 >> W;
        file1.close();
    } else {
        cerr << "Unable to open file " << endl;
    }

    // int W = 50; 
    // vector<Item> items = {{10, 60}, {20, 100}, {30, 120}}; 
    cout << "Maximum profit is " << knapsack(W, items) << endl;
    return 0;
}
