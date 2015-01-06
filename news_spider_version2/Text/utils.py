#coding=utf-8

import string

__author__ = 'galois'

def isNonWord(word):
    if word in string.punctuation:
        return True
    if word in "，：。，":
        return True
    return False