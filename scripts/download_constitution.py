import requests
import bs4
from pathlib import Path
import roman

START_STRING = "Recognizances, bonds, payable to people continue."
STOP_STRING = "Office of Legislative Legal Services, State Capitol Building, 200 E"
STARTURL = "http://tornado.state.co.us/gov_dir/leg_dir/olls/constitution.htm"

def download_all_articles(url):
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text)
    r.close()    
    
    text = " ".join(soup.get_text().split(START_STRING)[-1].split(STOP_STRING)[0].split()).strip()
    
    #One irregular capitalization of the term "section" in Article 2 throws off the section delimiter. 
    text = text.replace("Section of the Constitution shall", "section of the Constitution shall")
    
    preamble = text.split("ARTICLE")[0]
    articles = ["ARTICLE " + article.strip() for article in text.split("ARTICLE")[1:]]
    
    download_section("Preamble", "Preamble", preamble)
    for article in articles:
        article_number = "Article_" + str(roman.fromRoman(article.split(" ")[1].strip(". ")))
        if "Section " in article:
            download_all_sections(article, article_number)
        else: 
            download_section(article_number, article_number, article)
        
def download_all_sections(article_text, article_number):
    sections = ["Section " + section.strip() for section in article_text.split("Section ")[1:]]
    
    for section in sections:
        section_number = "Section " + section.split(" ")[1].strip(". ") 
        download_section(article_number, section_number, section)

def download_section(article_number, section_number, text):
    folder = "constitution/clean/" + article_number
    if not Path(folder).exists():
        Path(folder).mkdir(parents=True)
    outpath = Path(folder + "/" + section_number + ".txt")
    if outpath.exists():
        return
        
    with outpath.open('w', encoding='utf-8') as outf:
        outf.write(text) 

download_all_articles(STARTURL)        
    
        