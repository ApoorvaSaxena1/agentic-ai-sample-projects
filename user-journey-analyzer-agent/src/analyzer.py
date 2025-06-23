import pandas as pd
from visualizer import *
from recommender import generate_recommendations

def load_data(filepath):
    """Load clickstream CSV data."""
    try:
        data = pd.read_csv(filepath)
        print(f"✅ Loaded data with {len(data)} rows.")
        return data
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def analyze_user_journeys(data):
    """Print common user paths."""
    print("\n🔹 User journeys:")
    paths = data.groupby('user_id')['page'].apply(list)
    for user, path in paths.items():
        print(f"{user}: {' -> '.join(path)}")
    return paths

def format_stats_for_prompt(stats):
    lines = []
    for rest, r_data in stats.items():
        lines.append(f"Restaurant: {rest}")
        lines.append(f"  Page views: {r_data['views']}")
        for item, i_data in r_data['items'].items():
            lines.append(f"  Item: {item}")
            lines.append(f"    Views: {i_data['views']}")
            lines.append(f"    Added to cart: {i_data['adds']}")
            lines.append(f"    Cleared from cart: {i_data['clears']}")
            lines.append(f"    Checkouts: {i_data['checkouts']}")
    return "\n".join(lines)


def compute_menu_stats(data):
    """Compute views, adds, clears per restaurant + item"""
    stats = {}

    for _, row in data.iterrows():
        page = row['page']
        action = row['action']
        
        if 'restaurant_page:' in page:
            rest = page.split(': ')[1]
            stats.setdefault(rest, {'views': 0, 'items': {}})
            stats[rest]['views'] += 1
        
        elif 'menu_item_page:' in page:
            item = page.split(': ')[1]
            # Find restaurant from previous row (simple logic — could be improved)
            prev_rest = None
            for rev_idx in range(_, -1, -1):
                prev_page = data.iloc[rev_idx]['page']
                if 'restaurant_page:' in prev_page:
                    prev_rest = prev_page.split(': ')[1]
                    break
            if prev_rest:
                rest_stats = stats.setdefault(prev_rest, {'views': 0, 'items': {}})
                item_stats = rest_stats['items'].setdefault(item, {'views': 0, 'adds': 0, 'clears': 0, 'checkouts': 0})
                item_stats['views'] += 1
        
        elif page == 'cart' and action == 'add_item':
            # Assume last item added
            item = data.iloc[_ - 1]['page'].split(': ')[1]
            prev_rest = None
            for rev_idx in range(_, -1, -1):
                prev_page = data.iloc[rev_idx]['page']
                if 'restaurant_page:' in prev_page:
                    prev_rest = prev_page.split(': ')[1]
                    break
            if prev_rest:
                item_stats = stats[prev_rest]['items'].setdefault(item, {'views': 0, 'adds': 0, 'clears': 0, 'checkouts': 0})
                item_stats['adds'] += 1

        elif page == 'cart' and action == 'clear_cart':
            # Could assign to last restaurant — simplified logic
            for rest in stats:
                for item in stats[rest]['items'].values():
                    item['clears'] += 1
        
        elif page == 'checkout':
            # Could assign to last restaurant — simplified logic
            for rest in stats:
                for item in stats[rest]['items'].values():
                    item['checkouts'] += 1

    return stats


def identify_dropoffs(data):
    """Identify drop-off pages (where user journey ended)."""
    drop_offs = data.groupby('user_id').tail(1)['page'].value_counts()
    print("\n🔹 Drop-off pages:")
    print(drop_offs)
    return drop_offs

if __name__ == "__main__":
    # Input a big sample of data based on 200 sample users
    filepath = 'data/big_sample_clickstream.csv'

    # Input a small sample of data based on 20010 sample users
    # filepath = 'data/sample_clickstream.csv'
    
    data = load_data(filepath)
    stats = compute_menu_stats(data)
    stats_text = format_stats_for_prompt(stats)
    generate_sankey(data)
    generate_sunburst(data)
    generate_interactive_network(data)
    generate_flow_heatmap(data)
    if data is not None:
        paths = analyze_user_journeys(data)
        drop_offs = identify_dropoffs(data)
        
        # Pass to recommender (next step)
        
        generate_recommendations(paths, drop_offs, stats_text)

