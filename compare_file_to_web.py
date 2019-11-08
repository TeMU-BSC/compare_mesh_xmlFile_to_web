import xml.etree.ElementTree as ET
from natsort import natsorted, ns
from collections import defaultdict
from urllib.request import urlopen, urlretrieve
import sys
import os
import glob
import argparse
# Helps read xml, html,ect (dom) files and extract data easily.
from bs4 import BeautifulSoup

BASE_URL = 'https://pesquisa.bvsalud.org/portal/?output=xml&lang=pt&from=&sort=&format=&count=&fb=&page=1&index=tw&q=id%3A'


def compareAndSave(update_date1, update_date2, fileName1, fileName2, article_id1, article_id2, mh_list1, mh_list2, output_file):
    diff_mh1 = set(mh_list1-mh_list2)
    diff_mh2 = set(mh_list2-mh_list1)
    list(mh_list1).sort()
    list(mh_list2).sort()

    print(mh_list1)
    print(mh_list2)

    if diff_mh1 or diff_mh2:
        print("\nFound differents -> "+ fileName1," --- ", article_id1 +"\n",diff_mh1,"\n",diff_mh2,"\n")
        file_to_append = open(output_file, "a+")
        file_to_append.write(article_id1 + "\t" + str(update_date1) + "\t"+str("|".join(mh_list1)) + "\t" + str("|".join(diff_mh1)) + "\t" + fileName1 + "\n")
        file_to_append.write(article_id2 + "\t" + str(update_date2) + "\t"+str("|".join(mh_list2)) + "\t" + str("|".join(diff_mh2)) + "\t" + fileName2 + "\n")
        file_to_append.close()

def compareDocuments(xml_files_list,output_file, output_path_none_doc):

    # Loop for run a xml files one by one, from the xml files list.
    for i, file in enumerate(xml_files_list):
        print("\nFile -->",file,"---", i)

        xml_file = open(file)  # Open the xml file an save into the varibale.
        xml_content = xml_file.read()  # Read all content from xml file.
        
        bsObj = BeautifulSoup(xml_content, features='lxml') # Create a bson object of beautifulSoup.
        documents = bsObj.findAll("doc") # Getting all document from the bson object created before.

        for j, document in enumerate(documents):
            print("\nDoc -->", j)

            article_id = document.find(attrs={'name': "id"}).text
            update_date = document.find(attrs={'name': "update_date"}).text
            mh_children = document.find(attrs={'name': "mh"})

            if not mh_children:
                continue

            else:
                mesh_set = set()
                for mh_child in mh_children:
                    mesh_set.add(mh_child.text)
                sh_children = document.find(attrs={'name': "sh"})

                if sh_children:
                    for sh_child in mh_children:
                        mesh_set.add(sh_child.text)

                url = str(BASE_URL + article_id)

                xml_web_content = urlopen(url)
                bsObjWeb = BeautifulSoup(xml_web_content, features='lxml')
                documentWeb = bsObjWeb.find('doc')

                if not documentWeb:
                    file_doc_not_in_web = open(output_file, "a+")
                    file_doc_not_in_web.write(article_id+"\t"+ file + "\t" +url)
                    file_doc_not_in_web.close()
                    continue

                else:
                    article_idWeb = documentWeb.find(
                        text=article_id, attrs={'name': "id"}).text

                    mh_childrenWeb = documentWeb.find(attrs={'name': "mh"})
                    update_dateWeb = documentWeb.find(
                        attrs={'name': "update_date"}).text

                    if mh_childrenWeb:
                        mesh_setWeb = set()

                        for mh_childWeb in mh_childrenWeb:
                            mesh_setWeb.add(mh_childWeb.text)

                        sh_childrenWeb = documentWeb.find(attrs={'name': "sh"})

                        if sh_childrenWeb:
                            for sh_childWeb in sh_childrenWeb:
                                mesh_setWeb.add(sh_childWeb.text)

                    compareAndSave(update_date, update_dateWeb, file, url, article_id,
                                   article_idWeb, mesh_set, mesh_setWeb, output_file)


def main(input_dir, output_file,output_path_none_doc):
    list_files = glob.glob(os.path.join(input_dir, "*.xml"))

    list_files_sorted = natsorted(list_files, alg=ns.IGNORECASE)
    
    file_doc_not_in_web = open(output_path_none_doc, "w")
    file_doc_not_in_web.write("Article_id\tSource\tUrl")

    file_diff_doc = open(output_file, "w")
    file_diff_doc.write("Article_id\tUpdate Date\tMesh Headers\tDifferent\tSource\n")
    
    file_diff_doc.close()
    file_doc_not_in_web.close()

    compareDocuments(list_files_sorted,output_file,output_path_none_doc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='script_file_to_web.py', usage='%(prog)s [-i dir name] [-o file name]')
    parser.add_argument('-i', '--input', metavar='', required=True, type=str,
                        help='Input folder where it can find xml files. File must be finish with .xml .\n')
    parser.add_argument('-o', '--output', metavar='', type=str,
                        required=True, help='To define a name for outputs file.')

    args = parser.parse_args()

    input_dir = args.input
    output_path = args.output
    output_path_none_doc = output_path + "Doc_Not_Found_in_Web.txt"
    main(input_dir, output_path,output_path_none_doc)
