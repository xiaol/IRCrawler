#coding=utf-8
__author__ = 'galois'
from news_spider_version2.analyzer import jieba

class SimilarityCaculater:
    jieba.initialize()
    jieba.load_stopdict()
    w_title=0.9
    w_tag=0.1

    @classmethod
    def caculate(cls,item1,item2):
        sim_title=0.0
        if 'title' in item1 and 'title' in item2:
            sim_title=cls.caculateTitleSimilarity(item1['title'],item2['title'])
        sim_tag=cls.caculateTagSim(item1,item2)
        sim=cls.w_tag*sim_tag+cls.w_title*sim_title
        return sim

    @classmethod
    def caculateTagSim(cls,item1,item2):
        sim_tag=0
        for tag in item1['tag']:
            if tag in item2['tag']:
                sim_tag=sim_tag+1
        return sim_tag

    @classmethod
    def caculateTitleSimilarity(cls,title1,title2):
        listStr1=cls.getWordsList(title1)
        listStr2=cls.getWordsList(title2)
        return cls.caculateSimilarity(listStr1,listStr2)

    @classmethod
    def getWordsList(cls,strContent):
        if not strContent:
            return None
        wordList=[]
        for token in jieba.cut_with_stop(strContent,cut_all=False):
            wordList.append(token)
        return wordList

    @classmethod
    def caculateSimilarity(cls,listStr1,listStr2):
        if None==listStr1 and None==listStr2:
            return 1.0
        if None==listStr1:
            return 0.0
        if None==listStr2:
            return 0.0
        word_dict={}
        i=0
        for word in listStr1:
            word_dict[word]=i
        i=i+1
        for word in listStr2:
            if word not in word_dict:
                word_dict[word]=i
                i=i+1
        vect1=[]
        vect2=[]
        for j in range(0,i):
            vect1.append(0)
            vect2.append(0)
        for word in listStr1:
            pos=word_dict[word]
            vect1[pos]=1
        for word in listStr2:
            pos=word_dict[word]
            vect2[pos]=1

        inner_value=0.0
        vect_length1=0.0
        vect_length2=0.0
        for j in range(0,i):
            inner_value=inner_value+vect1[j]*vect2[j]
            vect_length1=vect_length1+vect1[j]
            vect_length2=vect_length2+vect2[j]

        if vect_length1==0 and  vect_length2==0:
            return 1.0
        if vect_length1==0 or vect_length2==0:
            return 0.0
        value= inner_value*inner_value/(vect_length1*vect_length2)
        return value

