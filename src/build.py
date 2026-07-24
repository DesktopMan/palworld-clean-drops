import json
import os
import shutil

from collections import defaultdict
from collections import UserDict

DIST_DIR = 'dist'
TARGET_PATH = os.path.join(DIST_DIR, 'raw')
TARGET_FILE = 'CleanDrops.json'
MONEY_THRESHOLD = 500


# Needed because casing is inconsistent in the Palworld data sets
class CaseInsensitiveDict(UserDict):
    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __contains__(self, key):
        return super().__contains__(key.lower())


def main():
    if os.path.isdir(DIST_DIR):
        shutil.rmtree(DIST_DIR)

    os.makedirs(TARGET_PATH)

    unwanted = CaseInsensitiveDict()

    with open('data/unwanted-items.txt') as f:
        for line in f:
            unwanted[line.strip()] = True

    with open('data/DT_PalDropItem_Common.json') as f:
        drops = json.load(f)

    prices = CaseInsensitiveDict()

    with open('data/DT_ItemDataTable_Common.json') as f:
        items = json.load(f)

        for item in items[0]['Rows'].items():
            item_id = item[0]

            if item_id in unwanted:
                prices[item_id] = round(item[1]['Price'] * 0.1 / 50) * 50  # Sell price

        missing_prices = set(unwanted) - set(prices.keys())
        if len(missing_prices) > 0:
            raise Exception(f'Failed to find prices for the following items: {missing_prices}')

    rows = drops[0]['Rows']
    filtered = {}
    item_counts = defaultdict(int)

    for source_id, row in rows.items():
        matched_slots = []
        for i in range(1, 11):
            item_id = row.get(f'ItemId{i}', 'None')
            if item_id in unwanted:
                matched_slots.append(i)
                item_counts[item_id] += 1

        if matched_slots:
            new_row = {}
            for i in matched_slots:
                price = prices[row[f'ItemId{i}']]

                if price >= MONEY_THRESHOLD:
                    new_row[f'ItemId{i}'] = 'Money'
                    new_row[f'min{i}'] = row[f'min{i}'] * prices[row[f'ItemId{i}']]
                    new_row[f'Max{i}'] = row[f'Max{i}'] * prices[row[f'ItemId{i}']]
                else:
                    new_row[f'ItemId{i}'] = 'None'
                    new_row[f'Rate{i}'] = 0
                    new_row[f'min{i}'] = 0
                    new_row[f'Max{i}'] = 0

            filtered[source_id] = new_row

    with open(os.path.join(TARGET_PATH, TARGET_FILE), 'w') as f:
        json.dump({'DT_PalDropItem_Common': filtered}, f, indent=2)

    print('Filter matches:')
    for item in sorted(item_counts.items(), key=lambda i: i[1]):
        price = prices[item[0]]

        print(f"{str(item[1]).rjust(3)} {item[0]} "
              f"({price}g, drops {price if price >= MONEY_THRESHOLD else 'nothing'})")


if __name__ == '__main__':
    main()
