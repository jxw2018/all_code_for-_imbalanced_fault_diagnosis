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
from tool.load_imbalanced_data import imbalanced_data,count_nums,accuracy,cnn_batches,accr_confusion_multiply,view_bar,ProgressBar
from tool.load_imbalanced_data import creat_sample_weight,shuffle_data
from keras.utils import to_categorical
from tensorflow.contrib.layers.python.layers import batch_norm
from imblearn.combine import SMOTETomek

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0" #指定使用的 GPU 编号为“0”
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)



class cnn_imbalanced(object):
    
    def __init__(self, input_x, output_y, is_training, keep_prob, input_num1, kernel_number_1, kernel_size_1, pooling_size_1, kernel_number_2, kernel_size_2, pooling_size_2, kernel_number_3, kernel_size_3, pooling_size_3, kernel_number_4, kernel_size_4, pooling_size_4, full_number, output_number):
        self.input_x = input_x
        self.output_y = output_y
        self.is_training = is_training
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
                  'layer_c2': tf.Variable(tf.truncated_normal([1, self.kernel_size_2, int((self.kernel_number_1)), self.kernel_number_2], stddev = k), name='c2'),
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
        
        layer_p1 = self.poolmax2d(layer_c11, pool_size = self.pooling_size_1)
        
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
        
        return out, loss_w, layer_fn
    
    def train(self, x, y, x_train_i, y_train_i, x_test_i, y_test_i, train_parameter):
        training_epochs = train_parameter['training_epochs']
        batch_size = train_parameter['batch_size']
        display_step = train_parameter['display_step']
        learning_rate = train_parameter['learning_rate']
        
        pred, loss_w, layer_fn = self.cost_cnn(x)
        pred_index = tf.argmax(pred, 1)
        y_index = tf.argmax(y, 1)
        confusion = tf.contrib.metrics.confusion_matrix(y_index, pred_index)
        y_index_accr = tf.reshape(y_index, [-1,1])
        y_index_accr = tf.to_int32(y_index_accr)
        accr_confusion = accuracy(confusion, y_index_accr, num_classes=8)
        g_mean = tf.pow(accr_confusion_multiply(accr_confusion, num_classes=8), 1/8)
        
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
        
        f_score_out = np.zeros(training_epochs)
        g_mean_out = np.zeros(training_epochs)
        f_score_out_test = np.zeros(training_epochs)
        g_mean_out_test = np.zeros(training_epochs)
        
        for i in range(training_epochs):
            avg_cost_train = 0.
            total_batch = int(x_train_i.shape[0]/batch_size)
            for batch_features, batch_labels in cnn_batches(batch_size, x_train_i, y_train_i):
                sess.run(optm1, feed_dict={x: batch_features, y: batch_labels, self.keep_prob: 0.5, self.is_training: True})
                avg_cost_train+=sess.run(cost1,feed_dict={x: batch_features, y: batch_labels, self.keep_prob:1.0, self.is_training: False})
            avg_cost = avg_cost_train/total_batch
            
            pred_index_f1 = sess.run(pred_index, feed_dict={x: x_test_i, self.keep_prob: 1.0, self.is_training: False})
            y_index_f1 = sess.run(y_index, feed_dict={y: y_test_i, self.keep_prob: 1.0, self.is_training: False})
            f_score_test = metrics.f1_score(y_index_f1, pred_index_f1, average='macro')
            f_score_out_test[i] = f_score_test
            
            pred_index_f1 = sess.run(pred_index, feed_dict={x: x_train_i, self.keep_prob: 1.0, self.is_training: False})
            y_index_f1 = sess.run(y_index, feed_dict={y: y_train_i, self.keep_prob: 1.0, self.is_training: False})
            f_score = metrics.f1_score(y_index_f1, pred_index_f1, average='macro')
            f_score_out[i] = f_score
        
            if i%display_step == 0:
                train_accr = sess.run(accr, feed_dict={x: x_train_i, y: y_train_i, self.keep_prob: 1.0, self.is_training: False})
                test_accr = sess.run(accr, feed_dict={x: x_test_i, y: y_test_i, self.keep_prob: 1.0, self.is_training: False})
                confusion_matrix = sess.run(confusion, feed_dict={x: x_test_i, y: y_test_i, self.keep_prob: 1.0, self.is_training: False})
                accr_confusion1 = sess.run(accr_confusion, feed_dict={x: x_train_i, y: y_train_i, self.keep_prob: 1.0, self.is_training: False})
                g_mean1 = sess.run(g_mean, feed_dict={x: x_train_i, y: y_train_i, self.keep_prob: 1.0, self.is_training: False})
                g_mean1_test = sess.run(g_mean, feed_dict={x: x_test_i, y: y_test_i, self.keep_prob: 1.0, self.is_training: False})
                g_mean_out[i] = g_mean1
                g_mean_out_test[i] = g_mean1_test
                print('\n step: %d cost: %.9f train accr: %.3f test accr: %.3f'%(i,avg_cost,train_accr,test_accr))
                
            
            if test_accr > 0.8:
                if test_accr < 0.82:
                    fn_output = sess.run(layer_fn, feed_dict={x: x_test_i, y: y_test_i, self.keep_prob: 1.0, self.is_training: False})
                    break
            
        return confusion_matrix, accr_confusion1, f_score_out, g_mean_out, test_accr, train_accr, f_score_out_test, g_mean_out_test, fn_output
    
    def conv2d(self, x, w, b, strides=1):
        x=tf.nn.conv2d(x, w, strides=[1, 1, strides, 1], padding= "VALID")
        x=tf.add(x, b)
        x=self.batch_norm_layer(x)
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
    imbalanced_dict = {0: 50, 1: 20, 2:20, 3:20, 4:5, 5:5, 6:5, 7:2}
#    imbalanced_dict = {0: 50, 1: 30, 2:30, 3:30, 4:15, 5:15, 6:15, 7:10}
#    imbalanced_dict = {0: 50, 1: 10, 2:10, 3:10, 4:3, 5:3, 6:3, 7:1}
    x_train_im, y_train_im, x_test_im, y_test_im, imbalanced_dict_1 = imbalanced_data(x_data, y_data, imbalanced_dict,refresh=False, seed=1)
    #x_train_i, y_train_i = shuffle_data(x_train_im, y_train_im)
    #x_test_i, y_test_i = shuffle_data(x_test_im, y_test_im)
    #np.savetxt("y_train_i.txt", y_train_i)
    #y_train_i = to_categorical(y_train_i)
    #y_test_i = to_categorical(y_test_i)
    smote_tomek = SMOTETomek(random_state=0)
    x_train_im, y_train_im = smote_tomek.fit_sample(x_train_im, y_train_im)
    
    
    
    x_train_i, y_train_i = shuffle_data(x_train_im, y_train_im)
    y_train_i = to_categorical(y_train_i)
    
    x_test_b, y_test_b = shuffle_data(x_test_b, y_test_b)
    
#    x_train_i = x_train_i[:,0:1920]
#    x_test_i = x_test_i[:,0:1920]
    
    return x_train_i, y_train_i, x_test_b, y_test_b


if __name__ == '__main__':
    x_train_i, y_train_i, x_test_i, y_test_i = data_process()
    
    acc_test = np.zeros(10)
    f_score_fin = np.zeros((10,50))
    g_mean_fin = np.zeros((10,50))
    f_score_fin_test = np.zeros((10,50))
    g_mean_fin_test = np.zeros((10,50))
    
    for i in range(1):
        x = tf.placeholder(tf.float32, [None, x_train_i.shape[1]])
        y = tf.placeholder(tf.float32, [None, y_train_i.shape[1]])
        keep_prob = tf.placeholder(tf.float32)
        is_training = tf.placeholder(dtype=tf.bool)
        
        model_name = 'cnn_imbalanced'
        if model_name == 'cnn_imbalanced':
            model = cnn_imbalanced(x, y,
                                   is_training,
                                   keep_prob,
                                   input_num1=1920,
                                   kernel_number_1=16,
                                   kernel_size_1=165,
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
                           'batch_size': 32, 
                           'display_step': 1,
                           'learning_rate': 0.001}
        
        print('%d experience is beginning... \n'%(i))
        confusion_matrix, accr_confusion1, f_score_out, g_mean_out, test_accr, train_accr, f_score_out_test, g_mean_out_test, fn_output = model.train(x, y, x_train_i, y_train_i, x_test_i, y_test_i, train_parameter)
        acc_test[i] = test_accr
        g_mean_fin[i] = g_mean_out
        f_score_fin[i] = f_score_out
        f_score_fin_test[i] = f_score_out_test
        g_mean_fin_test[i] = g_mean_out_test
        
        y_test_i = [np.argmax(one_hot)for one_hot in y_test_i]
        sio.savemat('fn_output', {'y': y_test_i, 'fn': fn_output})
        
        print('%d experience is ending... \n'%(i))
        
    
    