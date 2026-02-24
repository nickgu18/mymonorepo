import json
import matplotlib.pyplot as plt

def generate_graph():
    resolved_count = 0
    unresolved_count = 0
    empty_patch_count = 0
    total_count = 0

    with open('result.json', 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                status = data.get('status')
                if status == 'resolved':
                    resolved_count += 1
                elif status == 'unresolved':
                    unresolved_count += 1
                elif status == 'empty_patch':
                    empty_patch_count += 1
                total_count += 1
            except json.JSONDecodeError:
                # Skip empty or invalid lines
                pass

    not_resolved_count = unresolved_count + empty_patch_count
    
    if total_count > 0:
        resolved_percentage = (resolved_count / total_count) * 100
        not_resolved_percentage = (not_resolved_count / total_count) * 100

        labels = 'Resolved', 'Not Resolved'
        sizes = [resolved_percentage, not_resolved_percentage]
        explode = (0.1, 0)  # only "explode" the 1st slice (i.e. 'Resolved')

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.title("Percentage of Issues Resolved")
        plt.savefig('resolved_issues_percentage.png')
        print("Graph saved as resolved_issues_percentage.png")
    else:
        print("No data found in result.json")

if __name__ == '__main__':
    generate_graph()
