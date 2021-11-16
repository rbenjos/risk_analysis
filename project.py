import numpy as np
import pandas as pd

df = pd.read_csv("D:\Downloads\primary\primary.csv", chunksize=10000).get_chunk()
df.to_csv("D:\Downloads\primary\primary_small.csv")

