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
    
def HigherHighLowerLow(dataset):
    # calculate whether candle high extended higher than previous high. 1 - yes and 0 - no
    # calculate whether candle low extended lower than previous low. 1 - yes and 0 - no
    # calculate magnitude of excess extension equals to current high - previous high or current low - previous low    
    
    if not ("HigherHigh" in dataset.columns) and not ("LowerLow" in dataset.columns) and not ("ExcessHigh" in dataset.columns) and not ("ExcessLow" in dataset.columns):
        # obtain High and Low columns
        datasetNext = dataset[["High", "Low"]].copy()
        # decrement index by 1
        datasetNext.index = range(1, len(datasetNext) + 1)
        # join with original dataset using left join
        dataset.join(datasetNext, how="left", inplace=True, rsuffix="_prev")
        
        # generate mask for higher high and lower low
        higherHigh_mask = dataset["High"] > dataset["High_prev"]
        lowerLow_mask = dataset["Low"] < dataset["Low_prev"]
        
        # append columns
        dataset.loc[higherHigh_mask, "HigherHigh"] = 1
        dataset.loc[~higherHigh_mask, "HigherHigh"] = 0
        dataset.loc[lowerLow_mask, "LowerLow"] = 1
        dataset.loc[~lowerLow_mask, "LowerLow"] = 0
        dataset.loc[higherHigh_mask, "ExcessHigh"] = dataset["High"] - dataset["High_prev"] # absolute difference
        dataset.loc[lowerLow_mask, "ExcessLow"] = - dataset["Low"] + dataset["Low_prev"] # absolute difference
    else:
        print("HigherHigh and/or ExcessHigh and/or LowerLow and/or ExcessLow already exist in dataset")
        
    return

def main(datasetPath):
    # read dataset
    dataset = pd.read_csv(datasetPath, low_memory=False)
    
    # generate candle type feature
    candleType(dataset)
    
    # generate higher high and lower low flags and their excess highs and lows respectively
    HigherHighLowerLow(dataset)
    return

# create argument parser
argsParser = argparse.ArgumentParser(description="Function to apply transformations to a dataset of price movements represented by a candlestick chart")
argsParser.add_argument("dataset", help="Path to dataset")
args = argsParser.parse_args(sys.argv[1:])

# parse dataset path
datasetPath = args.__dict__["dataset"]

# run main function
main(datasetPath)