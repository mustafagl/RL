from tensorflow.keras import layers
from tensorflow import keras
import tensorflow as tf
import numpy as np
import random


class NN:

    def __init__(self,action_size,state_size):
        print(tf.config.list_physical_devices())
        gen_inputs = keras.Input(shape=state_size)
        gen_x = layers.Dense(64, activation='relu')(gen_inputs)
        gen_x = layers.Dense(32, activation='relu')(gen_x)
        gen_x = layers.Dense(16, activation='tanh')(gen_x)
        gen_outputs = layers.Dense(action_size, activation='softmax')(gen_x)
        self.generator = keras.Model(gen_inputs, gen_outputs, name='generator')


        dis_inputs = keras.Input(shape=state_size+action_size)
        dis_x = layers.Dense(64, activation='relu')(dis_inputs)
        dis_x = layers.Dense(64, activation='tanh')(dis_x)
        dis_outputs = layers.Dense(1, activation='sigmoid')(dis_x)
        self.discriminator = keras.Model(dis_inputs, dis_outputs, name='discriminator')

        # Define the GAN model which chains the generator and discriminator
        gan_inputs = keras.Input(shape=(state_size,))
        gan_outputs = self.discriminator(layers.concatenate([self.generator(gan_inputs),gan_inputs]))
        self.gan = keras.Model(gan_inputs, gan_outputs, name='gan')


        self.discriminator.compile(loss='binary_crossentropy', optimizer=keras.optimizers.Adam(learning_rate=0.0002, beta_1=0.5), metrics=['accuracy'])

        # Freeze the discriminator weights to train only the generator
        self.discriminator.trainable = False

        # Compile the GAN model
        self.gan.compile(loss='binary_crossentropy', optimizer=keras.optimizers.Adam(learning_rate=0.0002, beta_1=0.5))

    def train_network(self,first33,last33,u,epoch):
            
            batch_size = 128
            

            for idx in range(5):

                randidx = np.random.randint(0, np.array(u.state_buffer).shape[0], batch_size)

          

                unsucces_states = np.squeeze(np.array(u.state_buffer))
                succes_disc_in = np.squeeze(np.array(first33[-idx].disc_in_buffer))
                unsucces_disc_in = np.squeeze(np.array(u.disc_in_buffer))



                discriminator_loss_real = self.discriminator.train_on_batch(succes_disc_in[randidx], np.ones(batch_size))
                discriminator_loss_fake = self.discriminator.train_on_batch(unsucces_disc_in[randidx], np.zeros(batch_size))
                discriminator_loss = 0.5 * np.add(discriminator_loss_real, discriminator_loss_fake)


                generator_loss = self.gan.train_on_batch(unsucces_states[randidx], np.ones(batch_size))

                accuracy = self.discriminator.evaluate(succes_disc_in[randidx], np.ones(batch_size), verbose=0)[1]

                print(f"Epoch {epoch}, Discriminator Loss: {discriminator_loss[0]}, Generator Loss: {generator_loss},  Food: {first33[-1].food},  Accuracy: {accuracy}")



            """
            # Generate a single fake image by feeding random noise to the generator
            noise = np.random.normal(0, 1, (1, 100))
            fake_image = generator.predict(noise)

            # Train the discriminator on the real image
            real_image = x_train
            real_label = np.array([1])
            discriminator.train_on_batch(real_image, real_label)

            # Train the discriminator on the fake image
            fake_label = np.array([0])
            discriminator.train_on_batch(fake_image, fake_label)

            # Train the generator by trying to fool the discriminator
            noise = np.random.normal(0, 1, (1, 100))
            gan.train_on_batch(noise, real_label)
            
            # Print the losses every 100 epochs
            if epoch % 100 == 0:
                print(f"Epoch {epoch}, Discriminator Loss Real: {discriminator_loss_real}, Discriminator Loss Fake: {discriminator_loss_fake}, Generator Loss: {generator_loss}")

            """
