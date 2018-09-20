#coding:utf-8

import warnings
warnings.filterwarnings("ignore")
import jieba    
import numpy    
import codecs  
import re
import pandas as pd  
import matplotlib.pyplot as plt
from urllib import request
from bs4 import BeautifulSoup as bs
# %matplotlib inline
import matplotlib
matplotlib.rcParams['figure.figsize'] = (10.0, 5.0)
from wordcloud import WordCloud#词云包



#爬取评论函数
def getCommentsById(pageNum): 
    eachCommentList = []; 
    if pageNum>0: 
         start = (pageNum-1) * 100 
    else: 
        return False 

    # 话题链接，放要抓取的链接在这里，比如下面一个
    url_list = ['https://www.douban.com/group/topic/124232397/']

    for url in url_list:
        requrl = url +'?' +'start=' + str(start)
        print(requrl)
        resp = request.urlopen(requrl) 
        html_data = resp.read().decode('utf-8') 
        soup = bs(html_data, 'html.parser') 

        # comment_div_lits = soup.find_all('ul', class_='topic-reply') 
        comment_div_lits = soup.find_all('li', class_='clearfix comment-item') 
        # print(len(comment_div_lits))
    
        for item in comment_div_lits: 
            if item.find_all('p')[0].string is not None:     
                eachCommentList.append(item.find_all('p')[0].string)
            # print(eachCommentList)
            # # break
    return eachCommentList

def main():
    #循环话题的前n页评论
    commentList = []

    for i in range(4):    
        num = i + 1 
        commentList_temp = getCommentsById(num)
        commentList.append(commentList_temp)

    #将列表中的数据转换为字符串
    comments = ''
    for k in range(len(commentList)):
        comments = comments + (str(commentList[k])).strip()
    # print(comments)

    #使用正则表达式去除标点符号
    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    filterdata = re.findall(pattern, comments)
    cleaned_comments = ''.join(filterdata)
    # print(cleaned_comments)

    # #使用结巴分词进行中文分词
    segment = jieba.lcut(cleaned_comments)
    words_df=pd.DataFrame({'segment':segment})
    # print(words_df)

    # #去掉停用词
    stopwords=pd.read_csv("stopwords.txt",index_col=False,quoting=3,sep="\t",names=['stopword'], encoding='utf-8')#quoting=3全不引用
    words_df=words_df[~words_df.segment.isin(stopwords.stopword)]
    # print(words_df)

    # #统计词频
    words_stat=words_df.groupby(by=['segment'])['segment'].agg({"计数":numpy.size})
    words_stat=words_stat.reset_index().sort_values(by=["计数"],ascending=False)
    # print(words_stat)

    #用词云进行显示
    wordcloud=WordCloud(font_path="simhei.ttf",background_color="white",max_font_size=80)
    # wordcloud = WordCloud(background_color="white",width=1000, height=860, margin=2)
    word_frequence = {x[0]:x[1] for x in words_stat.head(1000).values}
    # print(type(word_frequence))
    word_frequence = sorted(word_frequence.items(), key=lambda kv: kv[1])
    # print(type(word_frequence))
    print(word_frequence)

    # word_frequence = word_frequence[:-20]
    # word_frequence_list = []
    # for key in word_frequence:
    #     temp = (key,word_frequence[key])
    #     word_frequence_list.append(temp)
    # print(word_frequence_list)                   # list
    # print(type(word_frequence_list[0]))          #tuple 

    # wordcloud=wordcloud.fit_words(word_frequence_list)
    # wordcloud = WordCloud().fit_words(word_frequence_list)

    wordcloud = wordcloud.fit_words(dict(word_frequence[:]))
    plt.imshow(wordcloud)
    plt.show()

#主函数
main()