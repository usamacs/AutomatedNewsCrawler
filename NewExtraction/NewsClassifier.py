#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pickle


class NewsClassifier:
    def __init__(self):
        self.group = None
        try:
            self.my_classifier = pickle.load(open('../my_clf_nb.pkl','rb'), encoding='latin1')
            print("Classifier Loaded Successfully...")
        except Exception as e:
            print("Classifier Loading Error...")
            print(e)


    def Predict_Group(self, content):
        try:
            predict_request = [content]
            predict_request = np.array(predict_request)
            y_hat = self.my_classifier.predict(predict_request)
            output = [y_hat[0]]
            self.group = str(output[0].decode("utf-8"))
        except Exception as e:
            print(e)
            self.group = None

        return self.group
