import requests
import json


def generate_outline_with_groq(api_key, cluster_id, cluster_data):
    keywords = [item["keyword"] for item in cluster_data]
    snippets = [item["serpapi_result"]["snippet"] for item in cluster_data if item.get("serpapi_result")]
    snippet_text = " ".join(snippets) if snippets else "No snippets available."
    prompt = f"""
Based on the following keywords and their web snippets, generate a **brief structured outline** in the format: intro, sections, conclusion. Keep each part **1-3 short sentences** maximum. Do not expand into detailed points.

Keywords: {', '.join(keywords)}
Web Snippets:
{snippet_text}

Output format:


Intro: ...


Sections: ...


Conclusion: ...


"""

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "system", "content": "You are an expert SEO content strategist."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
                             headers=headers, data=json.dumps(payload), timeout=60)
        resp.raise_for_status()
        data = resp.json()
        outline = data["choices"][0]["message"]["content"].strip()
        return {"cluster_id": cluster_id, "outline": outline}
    except Exception as e:
        print(f"Error generating outline for cluster {cluster_id}: {e}")
        return {"cluster_id": cluster_id, "outline": None}
