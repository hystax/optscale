from __future__ import absolute_import, division, print_function

import tensorflow as tf
import numpy as np

import optscale_arcee as arcee


# init arcee
arcee.init(token="test", application_key="linear_regression")

arcee.tag("project", "regression")

arcee.milestone("preparing data")

rng = np.random

learning_rate = 0.01
training_steps = 2000
display_step = 50

X = np.array(
    [
        3.3,
        4.4,
        5.5,
        6.71,
        6.93,
        4.168,
        9.779,
        6.182,
        7.59,
        2.167,
        7.042,
        10.791,
        5.313,
        7.997,
        5.654,
        9.27,
        3.1,
    ]
)
Y = np.array(
    [
        1.7,
        2.76,
        2.09,
        3.19,
        1.694,
        1.573,
        3.366,
        2.596,
        2.53,
        1.221,
        2.827,
        3.465,
        1.65,
        2.904,
        2.42,
        2.94,
        1.3,
    ]
)


W = tf.Variable(rng.randn(), name="weight")
b = tf.Variable(rng.randn(), name="bias")


def linear_regression(x):
    return W * x + b


def mean_square(y_pred, y_true):
    return tf.reduce_mean(tf.square(y_pred - y_true))


optimizer = tf.optimizers.SGD(learning_rate)


def run_optimization():
    with tf.GradientTape() as g:
        pred = linear_regression(X)
        loss = mean_square(pred, Y)
    gradients = g.gradient(loss, [W, b])
    optimizer.apply_gradients(zip(gradients, [W, b]))


arcee.milestone("calculation")

for step in range(1, training_steps + 1):
    run_optimization()

    if step % display_step == 0:
        pred = linear_regression(X)
        loss = mean_square(pred, Y)
        # send model stats
        arcee.send({"step": step, "loss": "%f" % loss})
        print("step: %i, loss: %f, W: %f, b: %f" % (step, loss, W.numpy(), b.numpy()))
arcee.milestone("calc done")
arcee.finish()
