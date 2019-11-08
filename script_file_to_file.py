import xml.etree.ElementTree as ET
from natsort import natsorted, ns
from collections import defaultdict
import sys
import glob
from bs4 import BeautifulSoup
import re

file_to_write = open("results_file.tsv", "w")
file_to_write.write("id\tsource\tupdate_date\tmh+sh\n")

def compareDocument(update_date1,update_date2,file1, file2, article_id1, article_id2, mh_list1, mh_list2):
    diff_mh = set(list(mh_list1-mh_list2) + list(mh_list2-mh_list1))
    print(mh_list1)
    print(mh_list2)

    if diff_mh:
        file_to_write.write(article_id1 + "\t"+file1 + "\t" + str(update_date1) + "\t"+str("|".join(mh_list1))+"\n")
        file_to_write.write(article_id2 + "\t"+file2 + "\t" + str(update_date2) + "\t"+str("|".join(mh_list2)) +"\n")
        print("\n----> Found different", diff_mh)


def findMatched(files_list1, files_list2):
    length_files = len(files_list1) 
    length_docs = length_files * 500

    for i, file in enumerate(files_list1):
        print("\n",length_files-i)
        xml_file = open(file)
        xml_content = xml_file.read()
        bsObj = BeautifulSoup(xml_content, features='lxml')
        documents = bsObj.findAll("doc")

        for i, document in enumerate(documents):
            print("\n",length_docs-i)
            article_id = document.find(attrs={'name': "id"}).text
            update_date1 = document.find(attrs={'name': "update_date"}).text

            mh_children = document.find(attrs={'name': "mh"})
   

            if mh_children:
                print("\nfile1 ->", file)
                print("article1-> ", article_id)
                mh_strings_list = set()

                for mh_child in mh_children:
                    mh_strings_list.add(mh_child.text)
                sh_children = document.find(attrs={'name': "sh"})
                if sh_children:
                    for sh_child in mh_children:
                        mh_strings_list.add(sh_child.text)
            else:
                continue

            for file2 in files_list2:

                print("\tfile2 -> ", file2)
                xml_file2 = open(file2)
                xml_content2 = xml_file2.read()
                bsObj2 = BeautifulSoup(xml_content2, features='lxml')

                id_tag2 = bsObj2.find(text=article_id, attrs={'name': "id"})

                if id_tag2:

                    article_id2 = id_tag2.text
                    document2 = id_tag2.find_parent('doc')
                    mh_children2 = document2.find(attrs={'name': "mh"})
                    update_date2 = document2.find(attrs={'name': "update_date"}).text
                    if mh_children2:
                        print("\tarticle2-> ", article_id2)
                        mh_strings_list2 = set()
                        for mh_child2 in mh_children2:
                            mh_strings_list2.add(mh_child2.text)
                        sh_children2 = document2.find(attrs={'name': "sh"})
                        if sh_children2:
                            for sh_child2 in mh_children2:
                                mh_strings_list2.add(sh_child2.text)

                    compareDocument(update_date1,update_date2, file, file2, article_id,
                                    article_id2, mh_strings_list, mh_strings_list2)
                    break


def main():
    list_files13sep = glob.glob("../13sep/*.xml")
    list_files30sep = glob.glob("../30sep/*.xml")

    list_files13sep_sorted = natsorted(list_files13sep, alg=ns.IGNORECASE)
    list_files30sep_sorted =  natsorted(list_files30sep, alg=ns.IGNORECASE)

    findMatched(list_files13sep_sorted, list_files30sep_sorted)


main()
