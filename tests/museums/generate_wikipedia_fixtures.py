import json
import sys
from museum_city.wikipedia_client import WikipediaClient

def main():
    client = WikipediaClient()
    # Fetch museum list page HTML
    html = client._fetch_page_html(client.MUSEUM_LIST_PAGE)
    with open("tests/museums/fixtures/museum_list.html", "w") as f:
        f.write(html)
    print("Saved museum list HTML")

    # Example city pages
    for title in ["Paris", "London", "New_York_City"]:
        city_html = client._fetch_page_html(title)
        with open(f"tests/museums/fixtures/{title}.html", "w") as f:
            f.write(city_html)
        print(f"Saved {title}")

if __name__ == "__main__":
    main()