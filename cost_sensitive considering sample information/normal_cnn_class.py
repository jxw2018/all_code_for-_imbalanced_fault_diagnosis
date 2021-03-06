# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 10:35:47 2019

@author: Administrator
"""

import tensorflow as tf
import scipy.io as sio
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn import metrics
from mpl_toolkits.mplot3d import Axes3D
from tool.load_imbalanced_data import imbalanced_data,calculate_class_weigh,create_class_weight,batches,norm_ZS,view_bar,ProgressBar
from tool.load_imbalanced_data import creat_sample_weight,shuffle_data
from keras.utils import to_categorical
from tensorflow.contrib.layers.python.layers import batch_norm

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0" #指定使用的 GPU 编号为“0”
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)



class cnn_imbalanced(object):
    
    def __init__(self, input_x, output_y, keep_prob, input_num1, kernel_number_1, kernel_size_1, pooling_size_1, kernel_number_2, kernel_size_2, pooling_size_2, kernel_number_3, kernel_size_3, pooling_size_3, kernel_number_4, kernel_size_4, pooling_size_4, full_number, output_number):
        self.input_x = input_x
        self.output_y = output_y
        self.keep_prob = keep_prob
        self.input_num1 = input_num1
        self.kernel_number_1=kernel_number_1
        self.kernel_size_1=kernel_size_1
        self.pooling_size_1=pooling_size_1
        self.kernel_number_2=kernel_number_2
        self.kernel_size_2=kernel_size_2
        self.pooling_size_2=pooling_size_2
        self.kernel_number_3=kernel_number_3
        self.kernel_size_3=kernel_size_3
        self.pooling_size_3=pooling_size_3
        self.kernel_number_4=kernel_number_4
        self.kernel_size_4=kernel_size_4
        self.pooling_size_4=pooling_size_4
        self.full_number=full_number
        self.output_number=output_number
        
                
    def weight_biases_cost(self):
        input_num=self.input_num1
        fc1_num=int((input_num-self.kernel_size_1+1)/self.pooling_size_1)
        fc1_num=int((fc1_num-self.kernel_size_2+1)/self.pooling_size_2)
        fc1_num=int((fc1_num-self.kernel_size_3+1)/self.pooling_size_3)
        fc1_num=int((fc1_num-self.kernel_size_4+1)/self.pooling_size_4)
        
        k = 0.05
        weight = {'layer_c11': tf.Variable(tf.truncated_normal([1, self.kernel_size_1, 1, self.kernel_number_1], stddev = k), name='c11'),
                  'layer_c12': tf.Variable(tf.truncated_normal([1, self.kernel_size_1, 1, self.kernel_number_1], stddev = k), name='c12'),
                  'layer_c13': tf.Variable(tf.truncated_normal([1, self.kernel_size_1, 1, self.kernel_number_1], stddev = k), name='c13'),
                  'layer_c2': tf.Variable(tf.truncated_normal([1, self.kernel_size_2, int(3*(self.kernel_number_1)), self.kernel_number_2], stddev = k), name='c2'),
                  'layer_c3': tf.Variable(tf.truncated_normal([1, self.kernel_size_3, self.kernel_number_2, self.kernel_number_3], stddev = k), name='c3'),
                  'layer_c4': tf.Variable(tf.truncated_normal([1, self.kernel_size_4, self.kernel_number_3, self.kernel_number_4], stddev = k), name='c4'),
                  'layer_fn1': tf.Variable(tf.truncated_normal([fc1_num*self.kernel_number_4, self.full_number], stddev = k), name='fc1'),
                  'layer_fn2': tf.Variable(tf.truncated_normal([self.full_number, self.full_number], stddev = k), name='fc2'),
                  'output': tf.Variable(tf.truncated_normal([self.full_number, self.output_number], stddev = k), name='c_out')}
        
        biases = {'layer_c11': tf.Variable(tf.truncated_normal([self.kernel_number_1], stddev = k), name='b11'),
                  'layer_c12': tf.Variable(tf.truncated_normal([self.kernel_number_1], stddev = k), name='b12'),
                  'layer_c13': tf.Variable(tf.truncated_normal([self.kernel_number_1], stddev = k), name='b13'),
                  'layer_c2': tf.Variable(tf.truncated_normal([self.kernel_number_2], stddev = k), name='b2'), 
                  'layer_c3': tf.Variable(tf.truncated_normal([self.kernel_number_3], stddev = k), name='b3'),
                  'layer_c4': tf.Variable(tf.truncated_normal([self.kernel_number_4], stddev = k), name='b4'),
                  'layer_fn1': tf.Variable(tf.truncated_normal([self.full_number], stddev = k), name='bc1'),
                  'layer_fn2': tf.Variable(tf.truncated_normal([self.full_number], stddev = k), name='bc2'),
                  'output': tf.Variable(tf.truncated_normal([self.output_number], stddev = k), name='b_out')}
                
        return weight, biases, fc1_num
        
    def cost_cnn(self, x):
        
        weight, biases, fc1_num = self.weight_biases_cost()
        lamba = 0.005
#        tf.add_to_collection('loss1', tf.contrib.layers.l2_regularizer(0.001)(weight['layer_c1']))
#        tf.add_to_collection('loss1', tf.contrib.layers.l2_regularizer(0.001)(weight['layer_c2']))
#        tf.add_to_collection('loss1', tf.contrib.layers.l2_regularizer(0.001)(weight['layer_c3']))
#        tf.add_to_collection('loss1', tf.contrib.layers.l2_regularizer(0.001)(weight['layer_c4']))
#        tf.add_to_collection('loss1', tf.contrib.layers.l2_regularizer(0.001)(weight['layer_fn1']))
#        tf.add_to_collection('loss1', tf.contrib.layers.l2_regularizer(0.001)(weight['output']))
        loss_w = tf.contrib.layers.l2_regularizer(lamba)(weight['layer_c11'])+tf.contrib.layers.l2_regularizer(lamba)(weight['layer_c12'])+tf.contrib.layers.l2_regularizer(lamba)(weight['layer_c13'])+tf.contrib.layers.l2_regularizer(lamba)(weight['layer_c2'])+tf.contrib.layers.l2_regularizer(lamba)(weight['layer_c3'])+tf.contrib.layers.l2_regularizer(lamba)(weight['layer_c4'])+tf.contrib.layers.l2_regularizer(lamba)(weight['layer_fn1'])+tf.contrib.layers.l2_regularizer(lamba)(weight['output'])
        
        
        x1 = x[:,0:1920]
        x2 = x[:,1920:3840]
        x3 = x[:,3840:5760]
        
        x1 = tf.reshape(x1, shape=[-1, 1, self.input_num1, 1])
        x2 = tf.reshape(x2, shape=[-1, 1, self.input_num1, 1])
        x3 = tf.reshape(x3, shape=[-1, 1, self.input_num1, 1])
        
        layer_c11 = self.conv2d(x1, weight['layer_c11'], biases['layer_c11'], strides=1)
        layer_c12 = self.conv2d(x2, weight['layer_c12'], biases['layer_c12'], strides=1)
        layer_c13 = self.conv2d(x3, weight['layer_c13'], biases['layer_c13'], strides=1)
        layer_c1 = tf.concat([layer_c11, layer_c12, layer_c13], 3)
        
        layer_p1 = self.poolmax2d(layer_c1, pool_size = self.pooling_size_1)
        
#        layer_p1_drop = tf.nn.dropout(layer_p1, self.keep_prob)
        
        #c2
        layer_c2 = self.conv2d(layer_p1, weight['layer_c2'], biases['layer_c2'], strides=1)
        layer_p2 = self.poolmax2d(layer_c2, pool_size = self.pooling_size_2) 
        
#        layer_p2_drop = tf.nn.dropout(layer_p2, self.keep_prob)
        
        #c3
        layer_c3 = self.conv2d(layer_p2, weight['layer_c3'], biases['layer_c3'], strides=1)
        layer_p3 = self.poolmax2d(layer_c3, pool_size = self.pooling_size_3) 
        
#        layer_p3_drop = tf.nn.dropout(layer_p3, self.keep_prob)
        
        #c4
        layer_c4 = self.conv2d(layer_p3, weight['layer_c4'], biases['layer_c4'], strides=1)
        layer_p4 = self.poolmax2d(layer_c4, pool_size = self.pooling_size_4) 
        
        #d1
        layer_p4_drop = tf.nn.dropout(layer_p4, self.keep_prob)
        
        #f1
        layer_fn = tf.reshape(layer_p4_drop, shape=[-1, fc1_num*self.kernel_number_4])
        layer_fn1 = tf.add(tf.matmul(layer_fn, weight['layer_fn1']), biases['layer_fn1'])
        layer_fn1 = tf.nn.relu(layer_fn1)
        
#        layer_fn2 = tf.add(tf.matmul(layer_fn1, weight['layer_fn2']), biases['layer_fn2'])
#        layer_fn2 = tf.nn.relu(layer_fn2)
        
        layer_fn1_drop = tf.nn.dropout(layer_fn1, self.keep_prob)
        
        #output layer
    #    out1 = tf.add(tf.matmul(layer_fn1_drop, weight['output']), biases['output'])
    #    out=tf.nn.softmax(out1)
        
        out1 = tf.add(tf.matmul(layer_fn1_drop, weight['output']), biases['output'])
        out = tf.nn.softmax(out1)
        
        return out, loss_w
    
    def train(self, x, y, x_train_i, y_train_i, x_test_i, y_test_i, train_weight, class_weight, ir_overall, train_parameter):
        training_epochs = train_parameter['training_epochs']
        batch_size = train_parameter['batch_size']
        display_step = train_parameter['display_step']
        learning_rate = train_parameter['learning_rate']
        
        pred, loss_w = self.cost_cnn(x)
        
        with tf.name_scope("loss"):
            cost1 = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))+loss_w
#            tf.add_to_collection('loss1', cost1)
#            cost2 = tf.add_n(tf.get_collection('loss1'))
            #cost=tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=pred, labels=y))
            optm1 = tf.train.AdamOptimizer(learning_rate = learning_rate, epsilon = 1e-8).minimize(cost1)
        
        corr = tf.equal(tf.argmax(y, 1), tf.argmax(pred, 1))
        accr = tf.reduce_mean(tf.cast(corr, tf.float64))
            
        sess = tf.Session()
        sess.run(tf.global_variables_initializer())
        
        for i in range(training_epochs):
            avg_cost_train = 0.
            total_batch = int(x_train_i.shape[0]/batch_size)
            for batch_features, batch_labels, weight_train in batches(batch_size, x_train_i, y_train_i, train_weight):
                sess.run(optm1, feed_dict={x: batch_features, y: batch_labels, self.keep_prob: 0.5})
                avg_cost_train+=sess.run(cost1,feed_dict={x: batch_features, y: batch_labels, self.keep_prob:1.0})
            avg_cost = avg_cost_train/total_batch
        
            if i%display_step == 0:
                train_accr = sess.run(accr, feed_dict={x: x_train_i, y: y_train_i, self.keep_prob: 0.5})
                #ff_score=sess.run(f_score,feed_dict={x:x_train_i,y:y_train_i,keep_prob:1.0})
                test_accr = sess.run(accr, feed_dict={x: x_test_i, y: y_test_i, self.keep_prob: 1.0})
#                print(sess.run(cost_weight))
                print('\n step: %d cost: %.9f train accr: %.3f test accr: %.3f'%(i,avg_cost,train_accr,test_accr))
                
        return test_accr
    
    def conv2d(self, x, w, b, strides=1):
        x=tf.nn.conv2d(x, w, strides=[1, 1, strides, 1], padding= "VALID")
        x=tf.add(x, b)
        return tf.nn.relu(x)

    def poolmax2d(self, x, pool_size=2):
        x=tf.nn.max_pool(x, ksize=[1, 1, pool_size, 1], strides=[1, 1, pool_size, 1], padding = "VALID")
        return x
    
    
    def batch_norm_layer(self, value, name='batch_norm'):
        if self.is_training is not False:
            return batch_norm(value, decay=0.9, updates_collections=None, is_training=True)
        else:
            return batch_norm(value, decay=0.9, updates_collections=None, is_training=False)

    
def data_process():
    
#    data = sio.loadmat('planetary_time_signal.mat')
#    x_data = data['planetary_feature']
#    y_data = data['planetary_feature_target']
    
    data = sio.loadmat('dataset.mat')
    x_data = data['f_data0']
    y_data = data['f_label']
    
    #x_data=norm_ZS(x_data)
    #balanced dataset
    x_train_b, x_test_b, y_train_b, y_test_b = train_test_split(x_data, y_data, test_size=0.2)
    
    #imbalanced dataset
#    imbalanced_dict = {0: 50, 1: 20, 2:20, 3:20, 4:5, 5:5, 6:5, 7:2}
    imbalanced_dict = {0: 50, 1: 30, 2:30, 3:30, 4:15, 5:15, 6:15, 7:10}
#    imbalanced_dict = {0: 50, 1: 10, 2:10, 3:10, 4:3, 5:3, 6:3, 7:1}
    x_train_im, y_train_im, x_test_im, y_test_im, imbalanced_dict_1 = imbalanced_data(x_data, y_data, imbalanced_dict,refresh=False, seed=1)
    #x_train_i, y_train_i = shuffle_data(x_train_im, y_train_im)
    #x_test_i, y_test_i = shuffle_data(x_test_im, y_test_im)
    #np.savetxt("y_train_i.txt", y_train_i)
    #y_train_i = to_categorical(y_train_i)
    #y_test_i = to_categorical(y_test_i)
    
    
    
    #%%computer class weight
    #sklearn class_weight
    #multi_class_weight=calculate_class_weigh(y_train)
    
    #own design class_weight
    multi_class_weight = create_class_weight(imbalanced_dict_1)
    split = 0.6
    multi_sample_weight, ir_overall = creat_sample_weight(imbalanced_dict_1, multi_class_weight, split)
    
    x_train_i, y_train_i = shuffle_data(x_train_im, y_train_im)
    xx_train, train_weight = shuffle_data(x_train_im, multi_sample_weight)
    train_weight = train_weight.reshape((len(train_weight), 1))
    x_test_i, y_test_i = shuffle_data(x_test_im, y_test_im)
    np.savetxt("y_train_i.txt", y_train_i)
    y_train_i = to_categorical(y_train_i)
    y_test_i = to_categorical(y_test_i)
    
    x_test_b, y_test_b = shuffle_data(x_test_b, y_test_b)
    
#    x_train_i = x_train_i[:,0:1920]
#    x_test_i = x_test_i[:,0:1920]
    
    return x_train_i, y_train_i, x_test_b, y_test_b, train_weight, ir_overall


if __name__ == '__main__':
    x_train_i, y_train_i, x_test_i, y_test_i, train_weight, ir_overall = data_process()
    
    acc_test = np.zeros(10)
    for i in range(10):
        x = tf.placeholder(tf.float32, [None, x_train_i.shape[1]])
        y = tf.placeholder(tf.float32, [None, y_train_i.shape[1]])
        class_weight = tf.placeholder(tf.float32, [None, 1])
        keep_prob = tf.placeholder(tf.float32)
        is_training = tf.placeholder(dtype=tf.bool)
        
        model_name = 'cnn_imbalanced'
        if model_name == 'cnn_imbalanced':
            model = cnn_imbalanced(x, y, 
                                   keep_prob,
                                   input_num1=1920,
                                   kernel_number_1=16,
                                   kernel_size_1=195,
                                   pooling_size_1=2,
                                   kernel_number_2=16,
                                   kernel_size_2=85,
                                   pooling_size_2=2,
                                   kernel_number_3=16,
                                   kernel_size_3=55,
                                   pooling_size_3=2,
                                   kernel_number_4=16,
                                   kernel_size_4=25,
                                   pooling_size_4=2,
                                   full_number=100,
                                   output_number=8)
        
        train_parameter = {'training_epochs': 50,
                           'batch_size': 80, 
                           'display_step': 1,
                           'learning_rate': 0.001}
        
    #    acc_test = np.zeros(10)
    #    for i in range(0,10):
        print('%d experience is beginning... \n'%(i))
        acc = model.train(x, y, x_train_i, y_train_i, x_test_i, y_test_i, train_weight, class_weight, ir_overall, train_parameter)
#        acc_test[i] = acc
        print('%d experience is ending... \n'%(i))
        
    
    