import csv
import random
from datetime import datetime, timedelta

restaurants = {
    "Pizza Palace": ["Margherita Pizza", "Pepperoni Pizza", "Garlic Bread"],
    "Sushi World": ["Salmon Roll", "Tuna Sashimi", "Miso Soup"],
    "Burger Barn": ["Cheeseburger", "Bacon Burger", "Fries"],
    "Vegan Vibes": ["Vegan Burger", "Quinoa Bowl", "Smoothie"],
    "Taco Town": ["Beef Taco", "Veggie Taco", "Nachos"],
    "BBQ Bliss": ["BBQ Ribs", "Pulled Pork Sandwich", "Cornbread"],
    "Noodle Nook": ["Chicken Chow Mein", "Spring Roll", "Fried Rice"],
    "Salad Studio": ["Caesar Salad", "Greek Salad", "Protein Bowl"],
    "Sweet Treats": ["Chocolate Cake", "Donut", "Ice Cream"]
}

actions = ["checkout", "clear_cart", "abandon"]

def generate_user_journey(user_id):
    journey = []
    time = datetime.now()

    # Homepage
    journey.append((user_id, time, "homepage", "view", 5))
    time += timedelta(seconds=5)

    # Visit 1-2 restaurants
    for _ in range(random.randint(1, 2)):
        rest = random.choice(list(restaurants.keys()))
        journey.append((user_id, time, f"restaurant_page: {rest}", "view", random.randint(5, 10)))
        time += timedelta(seconds=5)

        # View 1-3 items
        items_added = 0
        for _ in range(random.randint(1, 3)):
            item = random.choice(restaurants[rest])
            journey.append((user_id, time, f"menu_item_page: {item}", "view", random.randint(5, 10)))
            time += timedelta(seconds=5)

            # Randomly add to cart
            if random.random() < 0.7:
                journey.append((user_id, time, "cart", "add_item", 3))
                time += timedelta(seconds=3)
                items_added += 1

        # Maybe clear cart
        if items_added > 0 and random.random() < 0.3:
            journey.append((user_id, time, "cart", "clear_cart", 2))
            time += timedelta(seconds=2)

    # Final action
    if any(row[3] == "add_item" for row in journey):
        end = random.choices(
            ["checkout", "clear_cart", "abandon"],
            weights=[0.5, 0.2, 0.3],
            k=1
        )[0]
        if end == "checkout":
            journey.append((user_id, time, "checkout", "click", random.randint(5, 10)))
        elif end == "clear_cart":
            journey.append((user_id, time, "cart", "clear_cart", 2))
        else:
            # Abandon = no final cart/checkout action
            pass

    return journey

# Generate CSV
# Generate CSV with a smaller sample size
with open("data/big_sample_clickstream.csv", "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["user_id", "timestamp", "page", "action", "duration_on_page"])
    
    for i in range(1, 51):  # 100 users
        journey = generate_user_journey(f"u{i}")
        for row in journey:
            writer.writerow(row)

print("✅ Small complex sample data generated: 50 users!")

