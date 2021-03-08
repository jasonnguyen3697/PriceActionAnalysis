# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 15:00:37 2021

@introduction: commmodities such as shares, currency, metal, options, futures, etc. are traded everyday on the global market. Information about their price movemment is widely available, and can be used to guide trading actions {"Buy", "Sell", "No trade"}.

@purpose: the purpose of this script is to apply transformations to a dataset of price movements represented in candle sticks and calculate features/metrics of interest for analysis purposes.

@author: Jason
"""

import pandas as pd
import os
import numpy as np
import argparse
import sys

def candleType(dataset):
    # Generate candle type flag
    # Flag is Higher when close is higher than open, Lower when close is lower than open, and Doji when close is equal to open
    try:
        dataset["CandleType"]
        print("Column \"CandleType\" already exists in dataset")
        return
    except KeyError:
        # generate masks to calculate feature                
        higher_mask = dataset["Close"] > dataset["Open"]
        lower_mask = dataset["Close"] < dataset["Open"]
        doji_mask = dataset["Close"] == dataset["Open"]
        
        dataset.loc[higher_mask, "CandleType"] = 1
        dataset.loc[lower_mask, "CandleType"] = -1
        dataset.loc[doji_mask, "CandleType"] = 0
        
        return
    
def 

def main(datasetPath):
    # read dataset
    dataset = pd.read_csv(datasetPath, low_memory=False)
    
    # generate candle type feature
    candleType(dataset)
    
    # 
    return

# create argument parser
argsParser = argparse.ArgumentParser(description="Function to apply transformations to a dataset of price movements represented by a candlestick chart")
argsParser.add_argument("dataset", help="Path to dataset")
args = argsParser.parse_args(sys.argv[1:])

# parse dataset path
datasetPath = args.__dict__["dataset"]

# run main function
main(datasetPath)