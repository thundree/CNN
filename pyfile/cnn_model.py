import os
import math
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.python import ops
from tensorflow.python.layers.core import fully_connected


def initialize_convolution_kernel(conv_layers):
    """
    initialize convolution kernel
    :param conv_layers: a dict the key words like 'W1','W2', shape od
    :return: a dict that contains all filters of convolution
    """
    l = len(conv_layers)
    conv_kernel = {}

    for i in range(l):
        W = tf.compat.v1.get_variable('W'+str(i+1), conv_layers.get('W'+str(i+1)), initializer=tf.glorot_uniform_initializer())
        conv_kernel['W'+str(i+1)] = W

    return conv_kernel


def forward_propagation(X, conv_kernels, pool_strides, ksize, fully_neuron):
    """
    the forward propagation of convolution
    :param X: A placeholder which with shape(number_samples,height,weight,channels)
    :param conv_kernels: the conv_kernels, output of initialize_convolution_kernel
    :param pool_strides: the strides of max pool with each stride shape of (1,stride, stride,1)
    :param ksize: the pool size with each pool shape of(1, pool_size, pool_size, 1)
    :param fully_neuron: the neuron number of fully connected
    :return: the output of cnn
    """

    l = len(conv_kernels)
    A = X

    for i in range(l):
        # the kernel with shape of (filter_height, filter_width, in_channels, out_channels)
        Z = tf.nn.conv2d(A, conv_kernels['W'+str(i+1)], strides=[1, 1, 1, 1], padding='SAME')
        A = tf.nn.relu(Z)

        P = tf.nn.max_pool2d(A, ksize=ksize[i], strides=pool_strides[i], padding='SAME')

    flatten = tf.layers.flatten(P)
    y_hat = fully_connected(flatten, fully_neuron, activation=None)

    return y_hat


def compute_cost(y_hat, Y):
    """
    compute the cost of network
    :param y_hat: prediction value
    :param Y: the true label
    :return: cost
    """
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=y_hat, labels=Y))
    return cost


def model(train_x, train_y, test_x, test_y, conv_layer, pool_strides, ksize, fully_neuron, learning_rate=0.001, epochs=1000, batch_size=64, print_cost=True, plot_cost=True):
    """
    build the convolution network
    :param train_x: train data with shape of (number_samples,heights,weights, channels)
    :param train_y: the true label of train data
    :param test_x: the test data
    :param test_y: the test label
    :param conv_layer: the convolution layer each convolution kernel with shape of(height, weight, in_channels, out_channels)
    :param pool_strides: the pool layer strides each max-pooling with shape(1, strides, strides, 1)
    :param ksize: the pool layer filters size each filters with size of(1,
    :param fully_neuron:
    :param learning_rate:
    :param epochs:
    :param batch_size:
    :param print_cost:
    :param plot_cost:
    :return:
    """
    ops.reset_default_graph()

    # number of train samples, heights, weights, channels
    num_samples, n_h, n_w, n_c = train_x.shape
    n_y = train_y.shape[1]

    costs = []

    X = tf.placeholder(tf.float32, [None, n_h, n_w, n_c], name='input_x')
    Y = tf.placeholder(tf.float32, [None, n_y], name='output_y')

    conv_kernels = initialize_convolution_kernel(conv_layer)
    y_hat = forward_propagation(X, conv_kernels, pool_strides, ksize, fully_neuron)

    cost = compute_cost(y_hat, Y)
    optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=learning_rate)
    train_step = optimizer.minimize(cost)

    init_op = tf.compat.v1.global_variables_initializer()

    with tf.compat.v1.Session as sess:
        sess.run(init_op)

        for epoch in range(epochs):
            batch_cost = 0.0
            number_batches = int(num_samples // batch_size)
            batches = mini_batch(train_x, train_y, batch_size)

            for batch in batches:
                batch_x, batch_y = batch
                _, temp_cost = sess.run([train_step, cost], feed_dict={X: batch_x, Y: batch_y})
                batch_cost += temp_cost / number_batches

            pred = tf.equal(tf.argmax(y_hat, 1), tf.argmax(Y, 1))
            accuracy = tf.reduce_mean(tf.cast(pred, tf.float32))
            train_acc = accuracy.eval({X: train_x, Y: train_y})
            test_acc = accuracy.eval({X: test_x, Y: test_y})

            if print_cost is True and epoch % 10 == 0:
                print('Cost after epoch %i: %f' % (epoch, batch_cost))
            if plot_cost is True:
                costs.append(batch_cost)

            print('After iteration %i, train accuracy %.2f, test accuracy: %.2f' % (epoch, train_acc, test_acc))

        if plot_cost is True:
            plt.plot(np.squeeze(costs))
            plt.ylabel('cost')
            plt.xlabel('iterations (per tens)')
            plt.title('Learning rate = ' + str(learning_rate))
            plt.show()


def mini_batch(X, Y, batch_size):
    """
    extract number of batch_size samples
    :param X: train data with shape of (number_features, number_samples)
    :param Y: train label with shape of (number_class, number_samples), which is one_hot encode
    :param batch_size:
    :return: a list, which each element consist of (batch_x, batch_y)
    """
    m = X.shape[0]  # number of training samples
    batches = []

    # Shuffle (X, Y)
    permutation = list(np.random.permutation(m))
    shuffled_x = X[:, permutation]
    shuffled_y = Y[:, permutation]

    num_batches = math.floor(m / batch_size)
    for k in range(0, num_batches):
        batch_x = shuffled_x[k*batch_size: k*batch_size+batch_size, :, :, :]
        batch_y = shuffled_y[k*batch_size: k*batch_size+batch_size, :]
        batches.append((batch_x, batch_y))

    if m % batch_size != 0:
        batch_x = shuffled_x[num_batches * batch_size: m, :, :, :]
        batch_y = shuffled_y[num_batches * batch_size: m, :]
        batches.append((batch_x, batch_y))

    return batches


if __name__ == '__main__':
    os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
    pass