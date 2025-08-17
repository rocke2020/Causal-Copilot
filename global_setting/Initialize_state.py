from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any
import argparse
import pandas as pd
import ast
import numpy as np
import os
import json
import torch
from datetime import datetime
from global_setting.state import GlobalState
from data.simulator.simulation import SimulationManager
from llm import LLMClient
from utils.logger import logger



def load_data(global_state: GlobalState, args: argparse.Namespace):
    if args.simulation_mode == "online":
        simulation_manager = SimulationManager(args)
        config, data, graph = simulation_manager.generate_dataset()
    elif args.simulation_mode == "offline":
        if args.data_mode in ["simulated", "real"]:
            if os.path.isdir(args.data_file):
                config, data, graph = load_local_data(args.data_file)
            else: 
                data = pd.read_csv(args.data_file)
                config, graph = None, None
        # elif args.data_mode == "real":
        #     data = pd.read_csv(args.data_file)
        #     graph = None
        else:
            raise ValueError("Invalid data mode. Please choose 'real' or 'simulated'.")
    else:
        raise ValueError("Invalid simulation mode. Please choose 'online' or 'offline'.")
    
    global_state.user_data.raw_data = data
    global_state.user_data.ground_truth = graph

    # hard-coded heterogeneous and domain index, later would be set by the user query
    if 'domain_index' in data.columns:
        if data.nunique(axis=0)['domain_index'] > 1:
            global_state.statistics.heterogeneous = True
        else:
            global_state.statistics.heterogeneous = False
        global_state.statistics.domain_index = 'domain_index'

    return global_state

def load_local_data(directory: str):
    # Xinyue Wang Implemented
    '''
    :param directory: str for data directory
    :return: tuple of (config, data, graph)
    '''
    import json
    import os
    import pandas as pd
    import numpy as np

    if not os.path.exists(directory):
        raise FileNotFoundError(f"The directory {directory} does not exist.")

    config_path = f"{directory}/config.json"
    data_path = f"{directory}/base_data.csv"
    graph_path = f"{directory}/base_graph.npy"

    files = os.listdir(directory)

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config_path = None
        for file in files:
            if file.endswith(".json"):
                config_path = file
        if config_path != None:
            with open(os.path.join(directory, config_path), 'r') as f:
                config = json.load(f)
        else:
            config = None

    if os.path.exists(data_path):
        data = pd.read_csv(data_path)
    else:
        data_path = None
        for file in files:
            if file.endswith(".csv"):
                data_path = file
        if data_path != None:
            data = pd.read_csv(os.path.join(directory, data_path))
        else:
            raise FileNotFoundError(f"The data file {data_path} does not exist.")

    if os.path.exists(graph_path):
        graph = np.load(graph_path)
    else:
        graph_path = None
        for file in files:
            if file.endswith(".npy"):
                graph_path = file
        if graph_path != None:
            graph = np.load(os.path.join(directory, graph_path))
        else:
            graph = None

    return config, data, graph

def global_state_initialization(args: argparse.Namespace = None) -> GlobalState:
    user_query = args.initial_query
    global_state = GlobalState()

    global_state.user_data.initial_query = user_query

    # Extract information from user queries
    # get all available algorithms
    algorithms = [algo.split('.')[0] for algo in os.listdir('causal_discovery/context/algos') if algo.endswith('.txt') and 'tagging' not in algo and 'guideline' not in algo]  
    algorithms = ', '.join(algorithms)

    logger.debug(f"Available algorithms: {len(algorithms.split(', '))}", "Init")

    client = LLMClient(args)
    prompt = (f"Based on the query that I provided: {user_query} \n\n; "
              "extract the following information and summarize them in a json format, and output this json object."
              "Within the output, the key, the corresponding value options and their meanings are: \n\n "
              "1. Describe whether the relationship between the variables are assumed to be linear or not:"
              "Key: 'linearity'. \n\n"
              "Options of value (bool): True, False. \n\n"
              "2. Describe whether the fitting models between two variables, the error terms are assumed to be Gaussian or not:"
              "Key: 'gaussian_error'. \n\n"
              "Options of value (bool): True, False. \n\n"
              "3. The significance level (denoted as alpha) for doing statistical testing in the following analysis:"
              "Key: 'alpha'. \n\n"
              "Options of value (float): A numeric value that is greater than 0 and less than 1. \n\n"
              "4. Describe whether the dataset is heterogeneous or not:"
              "Key: 'heterogeneous'. \n\n"
              "Options of value (bool): True, False. \n\n"
              "5. If the dataset is heterogeneous, what is the name of the column in the dataset that represents the domain index:"
              "Key: 'domain_index'. \n\n"
              "Options of value (str): The name of the column that represents the domain index. \n\n"
              "6. Which algorithm the user would like to use to do causal discovery:"
              "Key: 'selected_algorithm'. \n\n"
              f"Options of value (str): {algorithms}. \n\n"
              "7. How many minutes the user can wait for the causal discovery algorithm:"
              "Key: 'waiting_minutes'. \n\n"
              "Options of value (float): A numeric value that is greater than 0. \n\n"
              "8. Does the user accept the output graph including undirected edges/undeterministic directions:"
              "Key: 'accept_CPDAG'. \n\n"
              "Options of value (bool, by default is True, only if the user explicitly asks for it to be False): True, False. \n\n"
              "9. Is the dataset a time-series dataset or a tabular dataset:"
              "Key: 'time_series'. \n\n"
              "Options of value (bool, by default is False, only if the user explicitly asks for it to be True): True, False. \n\n"
              "However, for each key, if the value extracted from queries does not match provided options, or if the queries do not provide enough information and you cannot summarize them,"
              "the value for such key should be set to None! \n\n"
              "Just give me the output in a json format, do not provide other information! \n\n")

    response = client.chat_completion(
        prompt=prompt,
        system_prompt="You are a helpful assistant. You are a causal discovery expert. You are given a user query and you need to extract the information from the query and return a json object.",
        json_response=True
    )
    info_extracted = response

    logger.info(f"Info extracted: {info_extracted}", "Init")

    # data management
    if args.demo_mode:
        run_dir = '/'.join(args.data_file.split('/')[:-1])
        global_state.user_data.output_report_dir = f'{run_dir}/output_report'
        global_state.user_data.output_graph_dir = f'{run_dir}/output_graph'
    else:
        date_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        global_state.user_data.output_report_dir = f'output/{args.data_file.split("/")[-1]}/{date_time}/output_report'
        global_state.user_data.output_graph_dir = f'output/{args.data_file.split("/")[-1]}/{date_time}/output_graph'

    # Assign extracted information from user queries to global_stat
    global_state.statistics.linearity = info_extracted["linearity"]
    global_state.statistics.gaussian_error = info_extracted["gaussian_error"]
    global_state.statistics.heterogeneous = info_extracted["heterogeneous"]
    global_state.statistics.domain_index = info_extracted["domain_index"]
    if global_state.statistics.domain_index is not None and global_state.statistics.domain_index not in global_state.user_data.raw_data.columns:
        global_state.statistics.domain_index = None
    global_state.algorithm.selected_algorithm = info_extracted["selected_algorithm"]
    global_state.statistics.time_series = info_extracted["time_series"]
    # GPU availability
    if torch.cuda.is_available():
        logger.info("Current machine supports CUDA, some algorithms can be accelerated by GPU if needed.", "Init")
    else:
        logger.warning("Current machine doesn't support CUDA, do not choose any GPU-powered algorithms.", "Init")
    global_state.statistics.gpu_available = torch.cuda.is_available()

    if info_extracted["waiting_minutes"] is not None:
        global_state.algorithm.waiting_minutes = info_extracted["waiting_minutes"]
    if info_extracted["alpha"] is not None:
        global_state.statistics.alpha = info_extracted["alpha"]

    # Accept CPDAG
    if info_extracted["accept_CPDAG"] is not None:
        global_state.user_data.accept_CPDAG = info_extracted["accept_CPDAG"]

    return global_state
