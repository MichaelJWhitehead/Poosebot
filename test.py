from bs4 import BeautifulSoup

with open("out.html", "r") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

for row in soup.find_all("tr"):
    cells = [td.get_text() for td in row.find_all("td")]
    if any("IT" in cell for cell in cells):
        print(cells)
