import numpy as np
import tensorflow as tf

class tf_single:
    __instance = None
    __graph = None
    __sess = None
    def __init__(self, hoge=None):
        if hoge is not None:
            self.create_graph(hoge)
    
    def __new__(cls, hoge=None):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__graph = {}
            cls.__sess = tf.Session()

        return cls.__instance

    def create_graph(self, hoge):
        if hoge in self.__graph.keys():
            return

        self.__graph[hoge]={}
        self.__graph[hoge]['X'] = tf.placeholder(tf.float32, [None, hoge])
        self.__graph[hoge]['Y'] = tf.placeholder(tf.float32, [None, hoge])

        X = self.__graph[hoge]['X']
        Y = self.__graph[hoge]['Y']

        result = piyopiyo

        self.__graph[hoge]['node'] = result

    def compute(self, fuga1, fuga2):
        hoge = fuga1.shape[-1]
        feed_dict={
            self.__graph[hoge]['X']:fuga1,
            self.__graph[hoge]['Y']:fuga2
            }
        result = self.__sess.run(self.__graph[hoge]['node'], feed_dict)
        return result

def tf_compute(fuga1, fuga2):
    hoge = fuga1.shape[-1]
    tf_obj = tf_single(hoge)
    D = tf_obj.compute(fuga1, fuga2)
    return D

