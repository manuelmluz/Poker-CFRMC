import csv
import pandas as pd

#training_data = pd.read_csv('training_data/cfr_training.csv')

def filter_default_strategies(input_csv, output_csv):
    with open(input_csv, 'r') as infile, open(output_csv, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        # headers
        header = next(reader)
        writer.writerow(header)
        #filter rows
        for row in reader:
            strategy = row[1].strip() 
            if strategy != "[0.33,0.33,0.33]":
                writer.writerow(row)

filter_default_strategies('training_data/cfr_training.csv', "cfr_training_data_clean.csv")