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
        datasetPrev = dataset[["High", "Low"]].copy()
        # increment index by 1
        datasetPrev.index = range(1, len(datasetPrev) + 1)
        # join with original dataset using left join
        dataset.join(datasetPrev, how="left", inplace=True, rsuffix="_prev")
        
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
        
        # drop _prev columns
        dataset.drop(labels=["High_prev", "Low_prev"], axis="columns", inplace=True)
    else:
        print("HigherHigh and/or ExcessHigh and/or LowerLow and/or ExcessLow already exist in dataset")
        
    return

def PivotPoints(dataset):
    # generate pivot point flag
    # definition of pivot points is:
    # high is higher than previous high and next high, low is higher than previous low and next low -> peak 1
    # low is lower than previous low and next low, high is lower than previous high and next high -> trough 0

    # create pivot point array where 0 means not a pivot point and 1 means is a pivot point
    if not ("Pivot" in dataset.columns) and not ("PivotType" in dataset.columns):
        # obtain next candle's higher high and lower low properties
        datasetNext = dataset[["HigherHigh", "LowerLow"]].copy()
        # decrement index by 1
        datasetNext.index = range(-1, len(datasetNext) - 1)
        # join with original dataset using left join
        dataset.join(datasetNext, how="left", inplace=True, rsuffix="_next")
        
        # generate mask for pivots
        peak_mask = (dataset["HigherHigh"]==1) & (dataset["LowerLow_next"]==1) & (dataset["HigherHigh_next"]==0)
        trough_mask = (dataset["LowerLow"]==1) & (dataset["HigherHigh_next"]==1) & (dataset["LowerLow_next"]==0)
        
        # append columns
        dataset.loc[peak_mask|trough_mask, "Pivot"] = 1
        dataset.loc[(~peak_mask)&(~trough_mask), "Pivot"] = 0
        dataset.loc[peak_mask, "PivotType"] = 1
        dataset.loc[trough_mask, "PivotType"] = 0
        
        # drop _next columns
        dataset.drop(labels=["HigherHigh_next", "LowerLow_next"], axis="columns", inplace=True)
    else:
        print("Pivot and/or PivotType columns already exist in dataset")
        
    return

def main(datasetPath):
    datasetOutputFolder, datasetName = os.path.split(datasetPath)
    
    # read dataset
    dataset = pd.read_csv(datasetPath, low_memory=False)
    
    # generate candle type feature
    candleType(dataset)
    
    # generate higher high and lower low flags and their excess highs and lows respectively
    HigherHighLowerLow(dataset)
    
    # generate pivot point flags
    PivotPoints(dataset)
    
    # output transformed dataset to same folder as input dataset
    datasetOutputPath = os.path.join(datasetOutputFolder, "_transformed.".join(datasetName.split(".")))
    dataset.to_csv(datasetOutputPath, index=False)
    
    return

# create argument parser
argsParser = argparse.ArgumentParser(description="Function to apply transformations to a dataset of price movements represented by a candlestick chart")
argsParser.add_argument("dataset", help="Path to dataset")
args = argsParser.parse_args(sys.argv[1:])

# parse dataset path
datasetPath = args.__dict__["dataset"]

# run main function
main(datasetPath)