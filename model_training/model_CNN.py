from keras.models import Model
from keras.layers import Dense, Input, Dropout, BatchNormalization, Conv2D, Flatten
from keras import regularizers
from keras.callbacks import Callback

def create_network_baseline(params):

    # Parameters
    input_shape = params['input_shape']

    num_conv_layers = params['num_conv_layers']
    kernels = params['kernels']
    kernel_size = params['kernel_size']


    num_FC_layers = params['num_FC_layers']
    num_FC_units = params['num_FC_units']

    dropout_rate = params['dropout_rate']
    Batch_norm_FLAG = params['Batch_norm_FLAG']
    Batch_norm_momentum = params['Batch_norm_momentum']

    l1_reg_weight = params['l1_regularizer_weight']

    # Layers
    input_layer = Input(input_shape)

    conv1 = Conv2D(kernels[0], kernel_size=kernel_size[0],
                   activity_regularizer=regularizers.l2(l1_reg_weight),
                   activation='relu')(input_layer)

    if Batch_norm_FLAG:
        conv1 = BatchNormalization(momentum=Batch_norm_momentum)(conv1)

    conv2 = Conv2D(kernels[1], kernel_size=kernel_size[1],
                   activation='relu',
                   activity_regularizer=regularizers.l2(l1_reg_weight))(conv1)

    if Batch_norm_FLAG:
        conv2 = BatchNormalization(momentum=Batch_norm_momentum)(conv2)

    conv_flat = Flatten()(conv2)

    FC1 = Dense(num_FC_units[0],
                activation='relu')(conv_flat)#,
                #activity_regularizer=regularizers.l2(l1_reg_weight))(FC1)
    FC1 = Dropout(dropout_rate)(FC1)

    if Batch_norm_FLAG:
        FC1 = BatchNormalization(momentum=Batch_norm_momentum)(FC1)

    FC2 = Dense(num_FC_units[1],
                activation='relu',
                activity_regularizer=regularizers.l2(l1_reg_weight))(FC1)
    FC2 = Dropout(dropout_rate)(FC2)

    if Batch_norm_FLAG:
        FC2 = BatchNormalization(momentum=Batch_norm_momentum)(FC2)

    output_layer = Dense(1, activation='sigmoid')(FC2)

    return Model(input_layer, output_layer, name='CNN')


def train(model, train_generator, val_generator, epochs=100, train_steps_per_epoch=100, val_steps_per_epoch=100):

    model.fit_generator(generator=train_generator,
                        steps_per_epoch=train_steps_per_epoch,
                        epochs=epochs,
                        verbose=2,
                        validation_data=val_generator,
                        validation_steps=val_steps_per_epoch)

    return model

def train_noDataGen(model, train_data, val_data, log_dir, epochs=100, batch_size=32):
#, train_steps_per_epoch=100):

    train_feats = train_data[0]
    train_labels = train_data[1]
    with open(log_dir + 'val_loss.txt', 'w') as log_file:
        hist = model.fit(train_feats, train_labels, batch_size=batch_size, epochs=epochs, callbacks=[ValCallback(val_data, log_file)])
    
    loss, acc = (hist.history['loss'], hist.history['acc'])
    #print(loss)
    #print(acc)
    print("Loss and accuracy file saved in {0}".format(log_dir))
    with open(log_dir + 'train_loss.txt', 'w') as o:
        for idx in range(epochs):
            o.writelines("{0} {1}\n".format(loss[idx], acc[idx]))
        
#, steps_per_epoch=train_steps_per_epoch)


class ValCallback(Callback):
    def __init__(self, val_data, log_file):
        self.val_data = val_data
        self.log_file = log_file

    def on_epoch_end(self, epoch, logs={}):
        x, y = self.val_data
        log_file = self.log_file
        loss, acc = self.model.evaluate(x, y, verbose=1)
        print('\nValidation loss: {}, acc: {}\n'.format(loss, acc))
        #with open(log_file, 'w') as o:
        log_file.write("{0} {1}\n".format(loss, acc))
