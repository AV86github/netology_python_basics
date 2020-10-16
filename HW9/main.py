import os
import json
import collections
import xml.etree.ElementTree as ET


def get_word_list(list_of_sent, word_len):
    return [word for item in list_of_sent for word in item.split()
            if len(word) > word_len]


def main():
    json_file = os.path.join(os.getcwd(), "newsafr.json")
    xml_file = os.path.join(os.getcwd(), "newsafr.xml")
    if os.path.isfile(json_file):
        print(f"====== JSON file: {json_file} ======")
        with open(json_file) as f:
            json_news = json.load(f)
        news = [x["description"] for x in json_news["rss"]["channel"]["items"]]
        news_words = get_word_list(news, 6)
        counter = collections.Counter(news_words)
        print("Top 10 common words:")
        print(counter.most_common(10))

    if os.path.isfile(xml_file):
        print(f"====== XML file: {xml_file} ======")
        tree = ET.ElementTree(file=xml_file)
        root = tree.getroot()
        news_xml = [x.find("description").text for x in root.findall(".//channel/item")]
        news_words_xml = get_word_list(news_xml, 6)
        counter_xml = collections.Counter(news_words_xml)
        print("Top 10 common words:")
        print(counter_xml.most_common(10))


if __name__ == '__main__':
    main()
