import os
import argparse
import tensorflow as tf
#import smdistributed.dataparallel.tensorflow as dist

class BirdAppTraining:
    
    def __init__(self, data_dir, model_dir, num_epochs=10, batch_size=32):
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        
        
    def _img_input(self, path):
        img = tf.io.read_file(path)
        img = tf.image.decode_png(img, channels=1)
        img = tf.cast(img, tf.float32) / 255.0
        return img

    @tf.function
    def _training_step(self, X, y, first_batch):
        
        with tf.GradientTape() as tape:
            pred = self.model(X, training=True)
            loss_value = self.loss(y, pred)
        
        #tape = dist.DistributedGradientTape(tape)
        grads = tape.gradient(loss_value, self.model.trainable_variables)
        self.opt.apply_gradients(zip(grads, self.model.trainable_variables))
        
        """
        if first_batch:
            dist.broadcast_variables(self.model.variables, root_rank=0)
            dist.broadcast_variables(self.opt.variables(), root_rank=0)
        """
        
        #loss_value = dist.oob_allreduce(loss_value)  
        #return loss_value
    
            
    def _training_loop(self):
        
        for epoch in range(self.num_epochs):
            print('epoch: ',epoch + 1)
            for batch in self.train:
                X, y = batch
                self._training_step(X, y, epoch == 0)

            acc = tf.keras.metrics.SparseCategoricalAccuracy()
            for batch in self.validation:
                X, y = batch
                print('val acc: ', acc(y_pred = self.model(X, training=False), y_true=y))

    def _build_model(self):
        input_layer = tf.keras.layers.Input(shape=(216, 514, 1))

        x = tf.keras.layers.Conv2D(64, (3, 3), padding='same')(input_layer)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.ReLU()(x)
        x = tf.keras.layers.MaxPooling2D((2, 2))(x)
        x = tf.keras.layers.Dropout(0.1)(x)

        x = tf.keras.layers.Conv2D(128, (3, 3), padding='same')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.ReLU()(x)
        x = tf.keras.layers.MaxPooling2D((2, 2))(x)
        x = tf.keras.layers.Dropout(0.1)(x)

        x = tf.keras.layers.Conv2D(256, (3, 3), padding='same')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.ReLU()(x)
        x = tf.keras.layers.MaxPooling2D((2, 2))(x)
        x = tf.keras.layers.Dropout(0.1)(x)

        x = tf.keras.layers.Conv2D(128, (3, 3) ,padding='same')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.ReLU()(x)
        x = tf.keras.layers.MaxPooling2D((2, 2))(x)
        x = tf.keras.layers.Dropout(0.1)(x)

        x = tf.keras.layers.GlobalAveragePooling2D()(x) 
        x = tf.keras.layers.Dense(256, activation='relu')(x)   
        x = tf.keras.layers.Dropout(0.3)(x) 
        x = tf.keras.layers.Dense(128, activation='relu')(x)   
        x = tf.keras.layers.Dropout(0.3)(x)

        output = tf.keras.layers.Dense(self.num_classes, activation='softmax')(x)
        model = tf.keras.Model(input_layer, output)
        return model

    def _load_data(self):

        X = []
        y = []

        cls_id_map = {}
        idx = 0

        for target_folder in os.listdir(self.data_dir):

            if target_folder not in cls_id_map:
                cls_id_map[target_folder] = idx
                idx += 1

            for img_name in os.listdir(self.data_dir +'/' + target_folder):
                img_path = self.data_dir + '/' + target_folder + '/' + img_name
                X.append(self._img_input(img_path))
                y.append(cls_id_map[target_folder])
        self.num_classes = len(cls_id_map)
        return X, y
    
    def create_dataset(self):
        X, y = self._load_data()
        data = tf.data.Dataset.from_tensor_slices((X, y))
        self.train = data.skip(3).shuffle(1000).batch(self.batch_size)
        self.validation = data.take(3).batch(self.batch_size)
        
    def model_training(self):
        self.model = self._build_model()
        self.loss = tf.losses.SparseCategoricalCrossentropy()
        self.opt = tf.optimizers.Adam(0.000125)
        self._training_loop()
    
    def save_model(self):
        self.model.save(os.path.join(self.model_dir, '000000001'))


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--model-dir', type=str, default=os.environ['SM_MODEL_DIR'])
    parser.add_argument('--train', type=str, default=os.environ['SM_CHANNEL_TRAIN'])
    
    args, _ = parser.parse_known_args()
    num_epochs = args.epochs
    sm_model_dir = args.model_dir
    training_dir= args.train
    
    """
    dist.init()
    gpus = tf.config.experimental.list_physical_devices("GPU")
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    if gpus:
        tf.config.experimental.set_visible_devices(gpus[dist.local_rank()], "GPU")
    """
    
    trainer = BirdAppTraining(data_dir=training_dir, model_dir=sm_model_dir, num_epochs=num_epochs)
    trainer.create_dataset()
    trainer.model_training()
    trainer.save_model()
    
    
