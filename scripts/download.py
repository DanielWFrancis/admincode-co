import requests
import bs4
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO)

STARTURL = "https://www.sos.state.co.us/CCR/NumericalDeptList.do"
DIRECTORY = "https://www.sos.state.co.us"
false_links = []

def get_soup(url):
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, "lxml")
    r.close()
    return soup

def download_all_divisions(url):
    soup = get_soup(url)
    div_links = [DIRECTORY + x["href"].replace(" ", "%20") for x in soup.find_all('a')
    if (x.find_parent('tr', class_="rowEven") or x.find_parent('tr', class_="rowOdd")) and len(x.get_text())>4]
    if url == STARTURL:
        for link in div_links:
            download_all_divisions(link)
    else:
        for link in div_links:
            download_rule_pdf(link)

def download_rule_pdf(url):
    soup = get_soup(url)
    #A javascript produces the links displayed on the page by concatenating the section's file_name
    #and ID, both of which are available in the page's HTML
    for x in soup.find_all('a', href="javascript:void(0)"):
        #print(str(x.parent['style']))
        if x.parent['style'] == "text-align: center;":
            if x:
                rule_tag = x
                version_id = rule_tag["onclick"].split("'")[1]
                file_name = rule_tag["onclick"].split("'")[3]
                date_effect = x.text.replace("/", "-")
                record_name = file_name.replace(" ", "_") + "__" + version_id + "__" + date_effect
                link = DIRECTORY + "/CCR/GenerateRulePdf.do?ruleVersionId=" + version_id + "&fileName=" + file_name.replace(" ", "%20")
            else:
                false_links.append(url)
                return

            folder = "data/raw/Agency_" + file_name.split(" ")[2].split("-")[0]
            if not Path(folder).exists():
                Path(folder).mkdir(parents=True)
            outpath = Path(folder + "/" + record_name + ".pdf")
            if not Path(outpath).exists():
                logging.info("Downloading {}".format(record_name))
                r = requests.get(link)
                with outpath.open('wb') as outf:
                   outf.write(r.content)
                r.close()
    return

download_all_divisions(STARTURL)
