# Federated-Learning-Approach-towards-Smart-Energy-Meter-Dataset
#python version:Python 3.10.13
#python-pip version:pip 23.2.1 from /home/william/repo/Federated-Learning-Approach-towards-Smart-Energy-Meter-Dataset/venv/lib/python3.10/site-packages/pip (python 3.10)

This project is part of Msc Thesis at Trinity College Dublin. 

The project focuses on simulating a Federated Learning framework using the London Household smart energy meter dataset. The primary objective is to achieve comparable accuracy in load forecasting to state-of-the-art (SOTA) technologies while demonstrating the preservation
of data privacy through FL. In real-world scenarios, the challenge of non-i.i.d. connections persists. To replicate real-world conditions, limited random connections are considered for each round of FL. Additionally, since smart meters often have limited computational
power, small sequential dense neural networks (DNN) are utilized to address this constraint. These DNN models are well-suited for low computational power devices and contribute to solving the computational challenges posed by smart meters. Through
this project, the aim is to showcase the potential of FL in maintaining data privacy while achieving accurate load forecasting results, even in resource-constrained environments.

Brief on the Project : (https://github.com/ADG4050/Federated-Learning-Approach-towards-Smart-Energy-Meter-Dataset/blob/Draft/Project%20Presentation.pdf)

The simulation is performed using Tensorflow Federated Libraries and Framework. To install TFF refer https://www.tensorflow.org/federated/install

Dataset Information : https://data.london.gov.uk/dataset/?q=energy

## The Methodology and Flow Diagrams used for this is below
<img src="Images\FD-1.png" width="800">
<img src="Images\FD-2.png" width="800">
<img src="Images\FD-3.png" width="800">

## Cluster 08 Results
Training Loss Results (MAE vs Federated Rounds) 
<img src="Images\TG-1.png" width="800">
<img src="Images\STY.png" width="800">
<img src="Images\STDF1.png" width="800">


## Code

The Code is divided into 5 parts
1) Data Cleaning and K - Means Application : <Code\datacl_kmeans_final.ipynb>
2) Short Term Daily Analysis code with custom loss function (MAIN CODE) : <Code\Short_Term_FC_custom_LF.ipynb>
3) Custom TFF Algorithms for checking Global and Local Weights : <Code\Customized_TFF_Functionalities.ipynb> 
4) Weekly Analysis Code : <Code\Weekly_Analysis.ipynb>
5) Monthly Analysis Code : <Code\Monthly_Analysis.ipynb>
6) Centralized Model Code : <Code\Centralized_model.ipynb>   

