from config import get_openai_api_key
from openai import OpenAI

def generate_recommendations(paths, drop_offs, stats_text):
    print("\n💡 AI-Powered Recommendations:")

    # Build summary text
    journey_examples = []
    for i, path in enumerate(paths.values):
        journey_examples.append(f"User {i+1}: {' -> '.join(path)}")
        if i >= 2:  # Limit to 3 examples
            break
    journeys_text = "\n".join(journey_examples)

    dropoff_text = ", ".join([f"{page} ({count} users)" for page, count in drop_offs.items()])

    prompt = f"""
    We have collected user activity data on a food delivery app. Here are the key stats:

    {stats_text}

    User journeys:
    {journeys_text}

    Drop-off points:
    {dropoff_text}

    Please analyze this data from the perspective of the restaurants. For each restaurant mentioned, provide:
    - A short summary of how users interacted with their page and menu
    - Any signs of friction (e.g. users adding items to cart but not checking out, clearing cart, abandoning at checkout)
    - Suggestions for the restaurant to improve conversions (e.g. promotions, clearer menu structure, better item descriptions)
    - Optional: Any app-level UI or flow recommendations that could improve the experience

    Be specific and actionable. Provide insights as if advising the restaurant owner or manager on how to increase orders.
    """

    try:
        api_key = get_openai_api_key()
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Switch from gpt-4
            messages=[
                {"role": "system", "content": "You are a helpful AI product assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )

        ai_reply = response.choices[0].message.content.strip()
        with open("outputs/ai_recommendations.md", "w", encoding="utf-8") as f:
            f.write(ai_reply)
        print(f"Generated {len(ai_reply.split())} words in AI recommendations.")
        
    except Exception as e:
        print(f"❌ Error calling OpenAI API: {e}")