import requests

def get_top_result_serpapi(keyword, api_key):
    params = {
        "engine": "google",
        "q": keyword,
        "api_key": api_key,
        "num": 1
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "organic_results" in data and len(data["organic_results"]) > 0:
            top_result = data["organic_results"][0]
            return {"link": top_result.get("link", ""), "snippet": top_result.get("snippet", "")}
    except Exception as e:
        print(f"Error fetching SerpAPI results for '{keyword}': {e}")
    return None
