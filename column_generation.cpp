#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <limits>

using namespace std;

struct Item {
    int demand;  
    int length;
};

struct Pattern {
    vector<int> cuts;
    int rollUsage;
};

double solveRMP(const vector<Pattern>& patterns, const vector<Item>& items, vector<double>& dualValues) {
    int numItems = items.size();
    int numPatterns = patterns.size();

    vector<double> dualVars(numItems, 0.0);
    double objectiveValue = 0.0;

    // calculate reduced cost for each pattern
    for (int i = 0; i < numPatterns; i++) {
        double patternCost = 0.0;
        for (int j = 0; j < numItems; j++) {
            patternCost += patterns[i].cuts[j] * dualValues[j];
        }
        objectiveValue += patternCost;
    }

    return objectiveValue;
}

Pattern generatePattern(const vector<Item>& items, int rollWidth, const vector<double>& dualValues) {
    int numItems = items.size();
    Pattern newPattern;
    newPattern.cuts.resize(numItems, 0);
    newPattern.rollUsage = 0;

    // greedy algorithm to maximize reduced cost
    for (int i = 0; i < numItems; i++) {
        if (dualValues[i] > 0 && newPattern.rollUsage + items[i].length <= rollWidth) {
            newPattern.cuts[i] = floor(dualValues[i]);
            newPattern.rollUsage += newPattern.cuts[i] * items[i].length;
        }
    }

    return newPattern;
}

int main() {
    int rollWidth = 110; 
    vector<Item> items = {{5, 20}, {7, 45}, {4, 50}};
    vector<Pattern> patterns = {{{5, 0, 0}, 100}, {{0, 2, 0}, 90}, {{0, 0, 2}, 100}};
    vector<double> dualValues(items.size(), 1.0);

    double epsilon = 0.01;

    while (true) {
        double objValue = solveRMP(patterns, items, dualValues);
        Pattern newPattern = generatePattern(items, rollWidth, dualValues);
        double reducedCost = 0.0;
        for (int i = 0; i < items.size(); i++) {
            reducedCost += newPattern.cuts[i] * dualValues[i];
        }
        reducedCost -= newPattern.rollUsage;

        if (reducedCost >= -epsilon) {
            break;
        }
        patterns.push_back(newPattern);
    }
    cout << "Optimal patterns:" << endl;
    for (const auto& pattern : patterns) {
        cout << "Pattern: ";
        for (int i = 0; i < items.size(); i++) {
            cout << pattern.cuts[i] << " ";
        }
        cout << " | Roll usage: " << pattern.rollUsage << endl;
    }

    return 0;
}
