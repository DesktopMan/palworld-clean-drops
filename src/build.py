import json
import os
import shutil


from collections import defaultdict

DIST_DIR = 'dist'
TARGET_PATH = os.path.join(DIST_DIR, 'raw')
TARGET_FILE = 'CleanDrops.json'


def main():
    # Clean
    if os.path.isdir(DIST_DIR):
        shutil.rmtree(DIST_DIR)

    os.makedirs(TARGET_PATH)

    with open('data/unwanted-items.txt') as f:
        unwanted = {line.strip() for line in f if line.strip()}

    with open('data/DT_PalDropItem_Common.json') as f:
        data = json.load(f)

    rows = data[0]['Rows']
    filtered = {}
    item_counts = defaultdict(int)

    for key, row in rows.items():
        matched_slots = []
        for i in range(1, 11):
            item_id = row.get(f'ItemId{i}', 'None')
            if item_id in unwanted:
                matched_slots.append(i)
                item_counts[item_id] += 1

        if matched_slots:
            new_row = {}
            for i in matched_slots:
                new_row[f'ItemId{i}'] = 'None'
                new_row[f'Rate{i}'] = 0.0
                new_row[f'min{i}'] = 0
                new_row[f'Max{i}'] = 0
            filtered[key] = new_row

    with open(os.path.join(TARGET_PATH, TARGET_FILE), 'w') as f:
        json.dump({'DT_PalDropItem_Common': filtered}, f, indent=2)

    print('Filter matches:')
    for item in sorted(item_counts.items(), key=lambda i: i[1]):
        print(str(item[1]).rjust(3) + ' ' + item[0])


if __name__ == '__main__':
    main()
