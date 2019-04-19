import tensorflow as tf


def loss_nl(labels, preds, years, add_summaries=True):
    '''Computes the mean squared-error between preds and labels,
    for the proper nightlights label.

    Args
    - labels: tf.Tensor, shape [batch_size], type float32
    - preds: tf.Tensor, shape [batch_size, 2], type float32
        1st column is DMSP prediction, 2nd column is VIIRS prediction
    - years: tf.Tensor, shape [batch_size], type int32
    - add_sumaries: bool, whether to create summaries for the loss variables

    Returns
    - loss_total: tf.Tensor, scalar, loss_mse + loss_reg
    - loss_mse: tf.Tensor, scalar, mean squared-error loss over the batch
    - loss_reg: tf.Tensor, scalar, regularization loss
    '''
    # DMSP for year < 2012, VIIRS for year >= 2012
    preds = tf.where(years < 2012, preds[:, 0], preds[:, 1])
    loss_mse = tf.losses.mean_squared_error(labels, preds)
    loss_total, loss_reg, loss_summaries = _loss_helper(
        loss_mse,
        loss_name='loss_mse',
        add_summaries=add_summaries)
    return loss_total, loss_mse, loss_reg, loss_summaries


def loss_mse(labels, preds, add_summaries=True):
    '''Computes the mean squared-error between preds and labels.

    Args
    - labels: tf.Tensor, shape [batch_size] or [batch_size, labels_dim]
    - preds: tf.Tensor, same shape as labels, type float32
    - add_sumaries: bool, whether to create summaries for the loss variables

    Returns
    - loss_total: tf.Tensor, scalar, loss_mse + loss_reg
    - loss_mse: tf.Tensor, scalar, mean squared-error loss over the batch
    - loss_reg: tf.Tensor, scalar, regularization loss
    '''
    loss_mse = tf.losses.mean_squared_error(labels, preds)
    loss_total, loss_reg, loss_summaries = _loss_helper(
        loss_mse,
        loss_name='loss_mse',
        add_summaries=add_summaries)
    return loss_total, loss_mse, loss_reg, loss_summaries


def loss_xent(labels, logits, add_summaries=True):
    '''Takes a softmax over logits, then calculates cross-entropy loss with the
    given labels.

    Args
    - labels: tf.Tensor, shape [batch_size], type int64, elements in [0, num_classes)
    - logits: tf.Tensor, shape [batch_size, num_classes], type float32
    - add_sumaries: bool, whether to create summaries for the loss variables

    Returns
    - loss_total: tf.Tensor, scalar, loss_xent + loss_reg
    - loss_xent: tf.Tensor, scalar, mean cross-entropy loss over the batch
    - loss_reg: tf.Tensor, scalar, regularization loss
    - loss_summaries: tf.summary if add_summaries is True, None otherwise
    '''
    loss_xent = tf.losses.sparse_softmax_cross_entropy(
        labels=labels,
        logits=logits,
        reduction=tf.losses.Reduction.SUM_BY_NONZERO_WEIGHTS)
    loss_total, loss_reg, loss_summaries = _loss_helper(
        loss_xent,
        loss_name='loss_cross_entropy',
        add_summaries=add_summaries)
    return loss_total, loss_xent, loss_reg, loss_summaries


def _loss_helper(loss, loss_name=None, add_summaries=False):
    '''Helper function to get total loss and regularization loss, and add summaries for
    all losses.

    Args
    - loss: tf.Tensor, scalar, the loss without regularization
    - loss_name: str, name for the loss summary
    - add_sumaries: bool, whether to create summaries for the loss variables

    Returns
    - loss_total: tf.Tensor, loss + loss_reg
    - loss_reg: tf.Tensor, the regularization loss
    - loss_summaries: tf.summary if add_summaries is True, None otherwise
    '''
    loss_total = tf.losses.get_total_loss(add_regularization_losses=True)
    loss_reg = tf.losses.get_regularization_loss()
    loss_summaries = None

    if add_summaries:
        loss_summaries = tf.summary.merge([
            tf.summary.scalar('loss_total', loss_total),
            tf.summary.scalar('loss_regularization_only', loss_reg),
            tf.summary.scalar(loss_name, loss)
        ])
    return loss_total, loss_reg, loss_summaries
