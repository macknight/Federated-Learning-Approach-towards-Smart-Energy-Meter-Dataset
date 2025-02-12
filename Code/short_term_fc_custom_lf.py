# -*- coding: utf-8 -*-
"""Short_Term_FC_custom_LF.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/macknight/Federated-Learning-Approach-towards-Smart-Energy-Meter-Dataset/blob/Draft/Code/Short_Term_FC_custom_LF.ipynb

## SHORT TERM DAILY FORECASTING - CLUSTERING + FEDERATED DNN APPROACH

TRAINING OF THE SEQUENTIAL MODELS IN FEDERATED SETUP
"""

#@test {"skip": true}

# Install or upgrade TensorFlow Federated library
# !pip install --quiet --upgrade tensorflow-federated

import collections
import numpy as np
import tensorflow as tf
import tensorflow_federated as tff

# Set a random seed for reproducibility
np.random.seed(0)

# Test the installation of TensorFlow Federated
tff.federated_computation(lambda: 'Hello, World!')()

# Mount Google Drive to access the data file
# from google.colab import drive
# drive.mount('/content/drive')

import pandas as pd

# Load the data from the CSV file into a Pandas DataFrame
data = pd.read_csv('/home/william/Cluster9data.csv')

# Convert the 'DateTime' column to datetime objects
data['DateTime'] = pd.to_datetime(data['DateTime'])

# Filter the DataFrame to include readings from 2011 to 2013
start_date1 = pd.to_datetime('2011-10-01')
end_date1 = pd.to_datetime('2013-02-28')
filtered_data1 = data[(data['DateTime'] >= start_date1) & (data['DateTime'] <= end_date1)]

# Select 20 unique LCLids
lclid_list1 = filtered_data1['LCLid'].unique()
selected_lclids1 = lclid_list1[:20]  # Select the first 20 unique LCLids

# Filter data for the selected LCLids
f_data1 = filtered_data1[filtered_data1['LCLid'].isin(selected_lclids1)]

# Create a copy of the filtered data for processing
datan1 = f_data1.copy()

# Convert the 'KWH/hh' column to float32 data type
datan1['KWH/hh'] = datan1['KWH/hh'].astype(np.float32)

# Drop the 'cluster' and 'stdorToU' columns from the DataFrame
datan1 = datan1.drop('cluster', axis=1)
datan1 = datan1.drop('stdorToU', axis=1)

# Reset the DataFrame index after dropping columns
datan1.reset_index(drop=True, inplace=True)

# Convert 'DateTime' column to datetime objects and remove timezone information
datan1['DateTime'] = pd.to_datetime(datan1['DateTime']).dt.tz_localize(None)

# Convert 'DateTime' to timestamp (Unix time in seconds) for each row
for i in range(len(datan1)):
    datan1['DateTime'][i] = datan1['DateTime'][i].timestamp()

# Convert 'DateTime' column to float32 data type
datan1['DateTime'] = datan1['DateTime'].astype(np.float32)

# Sort the data by 'LCLid' and 'DateTime' in ascending order
datan1.sort_values(['LCLid', 'DateTime'], inplace=True)

import collections

# Define the client window dataset function for a specific LCLid
def create_client_dataset_for_LCLid(client_data, window_size, step_size):
    client_windows = []    # List to store the input windows for the client
    client_targets = []    # List to store the target values for each window
    num_readings = len(client_data)    # Total number of readings for the client

    # Iterate over the readings using the sliding window
    for i in range(0, num_readings - window_size, step_size):
        window_start = i    # Start index of the window
        window_end = i + window_size - 1    # End index of the window
        prediction_index = window_end + step_size    # Index of the target value for the window

        # Extract the window and the prediction target
        window = client_data.iloc[window_start:window_end + 1]['KWH/hh'].values
        target = client_data.iloc[prediction_index]['KWH/hh']

        # Append the window and target to their respective lists
        client_windows.append(window)
        client_targets.append(target)

    # Create an ordered dictionary with 'x' and 'y' keys
    ordered_dict = collections.OrderedDict()
    ordered_dict['x'] = tf.stack(client_windows)    # Stack the windows as a tensor
    ordered_dict['y'] = tf.expand_dims(client_targets, axis=-1)    # Expand dimensions of target for compatibility

    return ordered_dict

# Define the window_size and step_size
window_size = 336
step_size = 1

# Filter the dataframe for the specific LCLid
example_LCLid = datan1['LCLid'].unique()[3]
clientyy_data = datan1[datan1['LCLid'] == example_LCLid]

# Create the client dataset for the specific LCLid
example_client_dataset = create_client_dataset_for_LCLid(clientyy_data, window_size, step_size)

# Print the results
print("Client dataset for LCLid", example_LCLid)
print(example_client_dataset)

NUM_EPOCHS = 5
BATCH_SIZE = 12
SHUFFLE_BUFFER = 60
PREFETCH_BUFFER = 6

def preprocess_client_dataset(dataset):
    def batch_format_fn(element):
        return collections.OrderedDict(
            x=tf.reshape(element['x'], [-1, 336]),
            y=tf.reshape(element['y'], [-1, 1]))
    return dataset.repeat(NUM_EPOCHS).shuffle(SHUFFLE_BUFFER).batch(
        BATCH_SIZE).map(batch_format_fn).prefetch(PREFETCH_BUFFER)

# Convert the example_client_dataset to a TensorFlow Dataset
preprocessed_example_client_dataset = preprocess_client_dataset(tf.data.Dataset.from_tensor_slices(example_client_dataset))

# Extract a sample batch from the preprocessed dataset
sample_batch = tf.nest.map_structure(lambda x: x.numpy(), next(iter(preprocessed_example_client_dataset)))

# Print the sample batch
print(sample_batch)

import random

NUM_CLIENTS = 15  # Replace with the desired number of clients
all_clients = datan1['LCLid'].unique()
sample_clients = random.sample(all_clients.tolist(), NUM_CLIENTS)

sample_clients_list = sample_clients
print(sample_clients_list)

# Iterate over unique LCLids in the dataframe
client_datasets_12 = {}
for LCLid in sample_clients_list:
    # Filter the dataframe for the current LCLid
    client_data = datan1[datan1['LCLid'] == LCLid]

    clientxx_dataset = create_client_dataset_for_LCLid(client_data, window_size, step_size)

    # Create the client dataset for the current LCLid
    preprocessed_client_dataset = preprocess_client_dataset(tf.data.Dataset.from_tensor_slices(clientxx_dataset))

    # Extract a sample batch from the preprocessed dataset
    sam_batch = tf.nest.map_structure(lambda x: x.numpy(), next(iter(preprocessed_client_dataset)))

    # Store the preprocessed dataset in the dictionary with LCLid as the key
    client_datasets_12[LCLid] = preprocessed_client_dataset

    # Uncomment the following lines if you want to print the sample batch for each client
    # print("Client dataset for LCLid", LCLid)
    # print(sam_batch)

def make_federated_data(client_datasets, sample_clients_list):
    return [
        client_datasets[x] for x in sample_clients_list
    ]

federated_train_data_12 = make_federated_data(client_datasets_12, sample_clients)

print(f'Number of client datasets: {len(federated_train_data_12)}')
# Output: Number of client datasets: 15

print(f'First dataset: {federated_train_data_12[0]}')
# Output: First dataset: <PrefetchDataset shapes: {x: (None, 336), y: (None, 1)}, types: {x: tf.float32, y: tf.float32}>

print(f'Second dataset: {federated_train_data_12[1]}')
# Output: Second dataset: <PrefetchDataset shapes: {x: (None, 336), y: (None, 1)}, types: {x: tf.float32, y: tf.float32}>

preprocessed_example_client_dataset.element_spec
# Output: {'x': TensorSpec(shape=(None, 336), dtype=tf.float32, name=None), 'y': TensorSpec(shape=(None, 1), dtype=tf.float32, name=None)}

# Function to create a Keras Sequential model for training on client datasets

def create_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(16, activation='relu', input_shape=(336,)),
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dense(4, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    return model

# Custom metric class for computing the mean metrics
class MeanMetrics(tf.keras.metrics.Metric):
    def __init__(self, name='mean_metrics', **kwargs):
        # Initialize the custom metric by inheriting from tf.keras.metrics.Metric class
        super(MeanMetrics, self).__init__(name=name, **kwargs)

        # Add the metric variables using add_weight method
        # mean_metrics stores the sum of differences between y_true and y_pred
        self.mean_metrics = self.add_weight(name='mean_metrics', initializer='zeros')

        # total_samples stores the total number of samples encountered
        self.total_samples = self.add_weight(name='total_samples', initializer='zeros')

    def update_state(self, y_true, y_pred, sample_weight=None):
        # Compute the difference between y_true and y_pred
        diff = y_true - y_pred

        # Compute the mean metric (mean of differences) for the current batch
        mean_metric = tf.reduce_mean(diff)

        # Get the number of samples in the batch (cast to float32 for division)
        num_samples = tf.cast(tf.shape(y_true)[0], tf.float32)

        # Accumulate the mean_metric multiplied by the number of samples
        self.mean_metrics.assign_add(mean_metric * num_samples)

        # Accumulate the total number of samples
        self.total_samples.assign_add(num_samples)

    def result(self):
        # Compute the final mean metric by dividing sum of mean_metric by total_samples
        return self.mean_metrics / self.total_samples

    def reset_states(self):
        # Reset the accumulated metric value and total samples count to zero
        self.mean_metrics.assign(0.0)
        self.total_samples.assign(0.0)

# Function to create a federated model using the custom MeanMetrics
def model_fn():
    # Create a Keras model using create_model function
    keras_model = create_model()

    # Define the loss function as MeanAbsoluteError
    loss = tf.keras.losses.MeanAbsoluteError()

    # Create a list of metrics, including the custom MeanMetrics
    metrics = [MeanMetrics()]

    # Convert the Keras model to a TFF model using tff.learning.models.from_keras_model
    tff_model = tff.learning.models.from_keras_model(
        keras_model,
        input_spec=preprocessed_example_client_dataset.element_spec,
        loss=loss,
        metrics=metrics
    )

    return tff_model

model = model_fn()
print(model)

# training starts
training_process = tff.learning.algorithms.build_weighted_fed_avg(
    model_fn,
    client_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=0.01),
    server_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=1.0))

# Inital GLoabal server state print
print(training_process.initialize.type_signature.formatted_representation())

train_state = training_process.initialize()

#TFF initialize and next functions for Federated Training
result = training_process.next(train_state, federated_train_data_12)
train_state = result.state
train_metrics = result.metrics
print('round  1, metrics={}'.format(train_metrics))

NUM_ROUNDS = 21
for round_num in range(2, NUM_ROUNDS):
  result = training_process.next(train_state, federated_train_data_12)
  train_state = result.state
  train_metrics = result.metrics
  print('round {:2d}, metrics={}'.format(round_num, train_metrics))

"""FEDERATED EVALUATION

"""

# Filter data for the specified time period (from 1st March 2013 to 28th February 2014)
start_date = '2013-03-01'
end_date = '2014-02-28'
filtered_data = data[(data['DateTime'] >= start_date) & (data['DateTime'] <= end_date)]

# Calculate the average KWH/hh for each LCLid using groupby and mean()
average_kwh = filtered_data.groupby('LCLid')['KWH/hh'].mean()

# Find the LCLids with the lowest, highest, and medium average KWH/hh
# idxmin() returns the LCLid with the lowest average KWH/hh
# idxmax() returns the LCLid with the highest average KWH/hh
# Sorting the average KWH/hh and finding the LCLid at the middle index gives the medium average LCLid
lowest_avg_lclid = average_kwh.idxmin()
highest_avg_lclid = average_kwh.idxmax()
medium_avg_lclid = average_kwh.sort_values().index[len(average_kwh) // 2]

# Print the LCLids with the lowest, highest, and medium average KWH/hh
print("LCLid with lowest average KWH/hh:", lowest_avg_lclid)
print("LCLid with highest average KWH/hh:", highest_avg_lclid)
print("LCLid with medium average KWH/hh:", medium_avg_lclid)

# Return the LCLids with the lowest, highest, and medium average KWH/hh
lowest_avg_lclid, highest_avg_lclid, medium_avg_lclid

# Calculate the average KWH/hh for each LCLid
average_kwh = filtered_data.groupby('LCLid')['KWH/hh'].mean()

# Print all LCLids with their corresponding average KWH/hh
for lclid, avg_kwh in average_kwh.items():
    print(f"LCLid: {lclid}, Average KWH/hh: {avg_kwh}")

# Enter Client ID on whose local data , evaluation will be performed
filtered_data44 = filtered_data[filtered_data['LCLid'] == 'MAC003247']

# Filter the data for 24th or 25th or 26th December 2013
filtered_data_24th_dec_2013 = filtered_data44[filtered_data44['DateTime'].dt.date == pd.to_datetime('2013-12-26').date()]

# Display the filtered data for 24th or 25th or 26th December 2013
print(filtered_data_24th_dec_2013)

# Change Date as per Requirement, start date 7 days prior of required date i.e end date
import datetime

teststart_date = pd.to_datetime('2013-12-19')
testend_date = pd.to_datetime('2013-12-26')

interval = datetime.timedelta(minutes=30)
num_datasets = 48

test_data = []  # List to store the test_data datasets

for i in range(num_datasets):
    start_time = teststart_date + i * interval
    end_time = testend_date + i * interval

    test_data_i = filtered_data44[
        (filtered_data44['DateTime'] >= start_time) & (filtered_data44['DateTime'] <= end_time)
    ]

    test_data.append(test_data_i)

# Initialize lists to store data for each iteration
lclid_lt = []  # List to store unique LCLids
sel_lclids = []  # List to store selected LCLids
ft_data = []  # List to store filtered data

# Iterate over the range 48
for i in range(48):
    # Select unique LCLids for the current iteration
    lclid_lt.append(test_data[i]['LCLid'].unique())

    # Select the first LCLid from the unique LCLids as the selected LCLid for the current iteration
    sel_lclids.append(lclid_lt[i][:1])

    # Filter data for the selected LCLid
    ft_data.append(test_data[i][test_data[i]['LCLid'].isin(sel_lclids[i])])

# Reset the index for each filtered data in ft_data, Convert the 'KWH/hh' column in each filtered
# data to float32, Drop the 'cluster' and 'stdorToU' columns from each filtered data in ft_data
for i in range(48):
    ft_data[i].reset_index(drop=True, inplace=True)
    ft_data[i]['KWH/hh'] = ft_data[i]['KWH/hh'].astype(np.float32)
    ft_data[i] = ft_data[i].drop('cluster', axis=1)
    ft_data[i] = ft_data[i].drop('stdorToU', axis=1)

# ft_data[5]
# Iterate over each DataFrame in ft_data
for df in ft_data:
    df['DateTime'] = pd.to_datetime(df['DateTime']).dt.tz_localize(None)
    df['DateTime'] = df['DateTime'].apply(lambda x: x.timestamp()).astype(np.float32)
    df.sort_values(['LCLid', 'DateTime'], inplace=True)

test_client = ft_data[7]['LCLid'].unique()

# test_client

test_dataset = []

# Iterate through the range of 48 elements
for i in range(48):
    # Initialize an empty dictionary for the current element
    element_data = {}

    # Iterate through each LCLid in test_client
    for LCLid in test_client:
        # Filter the dataframe for the current LCLid
        client_data = ft_data[i][ft_data[i]['LCLid'] == LCLid]

        # Create the client dataset for the current LCLid
        clientxx_dataset = create_client_dataset_for_LCLid(client_data, window_size, step_size)

        # Preprocess the client dataset
        preprocessed_client_dataset = preprocess_client_dataset(tf.data.Dataset.from_tensor_slices(clientxx_dataset))

        # Store the preprocessed dataset in the dictionary with LCLid as the key
        element_data[LCLid] = preprocessed_client_dataset

    # Append the element data to the test_dataset array
    test_dataset.append(element_data)

# test_dataset[6]

federated_test_data = []
for i in range(48):
  federated_test_data.append(make_federated_data(test_dataset[i], test_client))

evaluation_process = tff.learning.algorithms.build_fed_eval(model_fn)

print(evaluation_process.next.type_signature.formatted_representation())

evaluation_state = evaluation_process.initialize()
model_weights = training_process.get_model_weights(train_state)
evaluation_state = evaluation_process.set_model_weights(evaluation_state, model_weights)

evaluation_output = []
for i in range(48):
  evaluation_output.append(evaluation_process.next(evaluation_state, federated_test_data[i]))

# List to store all the loss values
loss_values_2 = []

# Append MAE values to the list
for i in range(48):
  loss_values_2.append(evaluation_output[i].metrics['client_work']['eval']['current_round_metrics']['mean_metrics'])

# Print the MAE values
print('loss_values_2')
print(loss_values_2)

# List to store all the loss values
loss_values_1 = []

# Append MAE values to the list
for i in range(48):
  loss_values_1.append(evaluation_output[i].metrics['client_work']['eval']['current_round_metrics']['loss'])

# Print the MAE values
print('loss_values_1')
print(loss_values_1)

# Actual Day Values
kwh_values_array = filtered_data_24th_dec_2013['KWH/hh'].values

# Display the array of 'KWH/hh' values
print('kwh_values_array')
print(kwh_values_array)

# Predicted Values = Actual Vlaues + loss
predicted_values = kwh_values_array + loss_values_2

# Display the predicted values array
print('predicted_values')
print(predicted_values)

# Plotting Graph to see the day forecast
import matplotlib.pyplot as plt
time_values = np.arange(len(kwh_values_array))

# Plot the actual values (kWh/hh) with blue color and label
plt.plot(time_values, kwh_values_array, color='blue', label='Actual Values (kWh/hh)')

# Plot the predicted values with red color and label
plt.plot(time_values, predicted_values, color='red', label='Predicted Values')

# Add labels and title
plt.xlabel('Time')
plt.ylabel('kWh/hh')
plt.title('Actual vs. Predicted Values')
plt.legend()

# Display the plot
plt.show()

# Create a DataFrame with the actual and predicted values
data = {
    'Actual Values (kWh/hh)': kwh_values_array,
    'Predicted Values': predicted_values
}

df = pd.DataFrame(data)

# Export the DataFrame to a CSV file
df.to_csv('/home/william/actual_vs_predicted.csv', index=False)
