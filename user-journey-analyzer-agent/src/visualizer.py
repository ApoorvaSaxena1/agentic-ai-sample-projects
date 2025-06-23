import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import networkx as nx
from pyvis.network import Network
import seaborn as sns


def plot_dropoff_bar(drop_offs, save_path='images/dropoff_chart.png'):
    """Plot a bar chart of drop-off page counts."""
    if drop_offs.empty:
        print("❌ No drop-off data to plot.")
        return
    
    drop_offs.plot(kind='bar', color='skyblue')
    plt.title('User Drop-off Pages')
    plt.xlabel('Page')
    plt.ylabel('Number of Users Dropping Off')
    plt.tight_layout()
    
    plt.savefig(save_path)
    print(f"✅ Drop-off bar chart saved to {save_path}")
    plt.close()

def generate_sankey(data, save_path='images/user_journey_sankey.html'):
    """Generate Sankey diagram with clean labels (no prefixes)."""

    # Group user journeys
    user_paths = data.groupby('user_id')['page'].apply(list)

    # Build link counts
    link_counter = {}
    for path in user_paths:
        clean_path = []
        for page in path:
            if 'restaurant_page:' in page:
                clean_page = page.split(': ')[1]
            elif 'menu_item_page:' in page:
                clean_page = page.split(': ')[1]
            else:
                clean_page = page
            clean_path.append(clean_page)

        for i in range(len(clean_path) - 1):
            pair = (clean_path[i], clean_path[i + 1])
            link_counter[pair] = link_counter.get(pair, 0) + 1

    # Create node list and map to indices
    nodes = list(set([p for pair in link_counter.keys() for p in pair]))
    node_idx = {name: idx for idx, name in enumerate(nodes)}

    # Build Sankey links
    source = [node_idx[src] for (src, tgt) in link_counter.keys()]
    target = [node_idx[tgt] for (src, tgt) in link_counter.keys()]
    value = list(link_counter.values())

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    )])

    fig.update_layout(title_text="User Journey Sankey Diagram", font_size=10)
    fig.write_html(save_path)
    print(f"✅ Sankey diagram saved to {save_path}")

def generate_sunburst(data, save_path='images/user_journey_sunburst.html'):
    """Generate a sunburst chart of user journeys with clean labels and cart node color."""

    grouped = data.groupby('user_id')['page'].apply(list)

    records = []
    for path in grouped:
        clean_path = []
        for page in path:
            if 'restaurant_page:' in page:
                clean_page = page.split(': ')[1]
            elif 'menu_item_page:' in page:
                clean_page = page.split(': ')[1]
            else:
                clean_page = page
            clean_path.append(clean_page)

        padded = clean_path + [''] * (5 - len(clean_path))
        records.append(padded[:5])

    path_df = pd.DataFrame(records, columns=['step1', 'step2', 'step3', 'step4', 'step5'])
    path_df['count'] = 1

    agg_df = path_df.groupby(['step1', 'step2', 'step3', 'step4', 'step5']).count().reset_index()

    # Combine all step columns to create a flattened list of unique node labels
    labels = pd.concat([
        agg_df['step1'], agg_df['step2'], agg_df['step3'],
        agg_df['step4'], agg_df['step5']
    ]).unique()

    # Build color map: assign red to cart, let Plotly auto-assign others
    color_map = {}
    for label in labels:
        if label == 'cart':
            color_map[label] = 'red'
        else:
            color_map[label] = None  # Will default to Plotly's palette

    # Build sunburst, apply colors based on each node's label
    fig = px.sunburst(
        agg_df,
        path=['step1', 'step2', 'step3', 'step4', 'step5'],
        values='count',
        color='step5',  # Or any step that could contain cart or menu items
        color_discrete_map=color_map,
        title='User Journey Sunburst'
    )

    fig.write_html(save_path)
    print(f"✅ Sunburst chart saved to {save_path}")


def generate_interactive_network(data, save_path='images/user_journey_network.html'):
    G = nx.DiGraph()
    grouped = data.groupby('user_id')['page'].apply(list)

    edge_counter = {}
    node_types = {}

    for path in grouped:
        cleaned_path = []
        for page in path:
            if 'restaurant_page:' in page:
                name = page.split(': ')[1]
                cleaned_path.append(name)
                node_types[name] = 'restaurant'
            elif 'menu_item_page:' in page:
                name = page.split(': ')[1]
                cleaned_path.append(name)
                node_types[name] = 'menu_item'
            else:
                cleaned_path.append(page)
                node_types[page] = 'other'

        for i in range(len(cleaned_path) - 1):
            pair = (cleaned_path[i], cleaned_path[i+1])
            edge_counter[pair] = edge_counter.get(pair, 0) + 1

    # Build graph
    for (src, tgt), weight in edge_counter.items():
        G.add_edge(src, tgt, weight=weight)

    net = Network(height="600px", width="100%", directed=True)
    color_map = {
        'restaurant': 'orange',
        'menu_item': 'lightgreen',
        'other': 'lightblue'
    }

    for node in G.nodes:
        ntype = node_types.get(node, 'other')
        net.add_node(node, label=node, color=color_map[ntype])

    for src, tgt, data in G.edges(data=True):
        net.add_edge(src, tgt, value=data['weight'], title=f"{src} → {tgt}: {data['weight']} users")

    # Add a legend using dummy nodes
    net.add_node("Legend: Restaurant", shape="box", color="orange", hidden=True)
    net.add_node("Legend: Menu Item", shape="box", color="lightgreen", hidden=True)
    net.add_node("Legend: Other", shape="box", color="lightblue", hidden=True)

    net.show_buttons(filter_=['physics'])
    net.show(save_path)
    print(f"✅ Interactive network map saved to {save_path}")

def generate_path_frequency_bar(data, save_path='images/path_frequency_bar.png'):
    grouped = data.groupby('user_id')['page'].apply(lambda x: ' -> '.join(x))
    counts = grouped.value_counts().head(10)

    counts.plot(kind='barh', figsize=(10, 6), color='skyblue')
    plt.xlabel('Number of Users')
    plt.title('Top 10 User Paths')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"✅ Path frequency bar chart saved to {save_path}")

def generate_flow_heatmap(data, save_path='images/flow_heatmap.png'):
    """Create a heatmap showing frequency of menu items at each customer journey step."""

    grouped = data.groupby('user_id')['page'].apply(list)

    records = []
    for path in grouped:
        step_num = 1
        for page in path:
            if 'menu_item_page:' in page:
                # Extract clean item name
                item = page.split(': ')[1]
                records.append({'step': step_num, 'item': item})
            step_num += 1

    if not records:
        print("⚠️ No menu item views found in data.")
        return

    df = pd.DataFrame(records)

    # Create pivot table: rows = menu items, cols = step number, values = user counts
    pivot = df.pivot_table(index='item', columns='step', aggfunc='size', fill_value=0)

    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt='d', cmap='YlGnBu')
    plt.title('Menu Item Popularity by Customer Step')
    plt.ylabel('Popular Menu Items')
    plt.xlabel('Customers')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"✅ Flow heatmap saved to {save_path}")