import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

# Sentiment Data Processing
def process_sentiment_data(file_path):
    sentiment_data = pd.read_csv(file_path)
    # Assuming the file has columns 'date' and 'sentiment_score'
    sentiment_data['date'] = pd.to_datetime(sentiment_data['date'])
    return sentiment_data

# Financial Data Processing
def process_financial_data(file_path):
    financial_data = pd.read_csv(file_path)
    # Assuming the file has columns 'date', 'TVL', and 'fees'
    financial_data['date'] = pd.to_datetime(financial_data['date'])
    return financial_data

# Time Frame Alignment
def align_data(sentiment_data, financial_data):
    aligned_data = pd.merge(sentiment_data, financial_data, on='date', how='inner')
    return aligned_data

# Correlation Computation
def calculate_correlation(aligned_data):
    pearson_tvl = pearsonr(aligned_data['sentiment_score'], aligned_data['TVL'])
    spearman_tvl = spearmanr(aligned_data['sentiment_score'], aligned_data['TVL'])

    pearson_fees = pearsonr(aligned_data['sentiment_score'], aligned_data['fees'])
    spearman_fees = spearmanr(aligned_data['sentiment_score'], aligned_data['fees'])

    return (pearson_tvl, spearman_tvl, pearson_fees, spearman_fees)

# Graphical Representation
def plot_data(aligned_data):
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Sentiment Score', color=color)
    ax1.plot(aligned_data['date'], aligned_data['sentiment_score'], color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  
    color = 'tab:blue'
    ax2.set_ylabel('TVL and Fees', color=color)
    ax2.plot(aligned_data['date'], aligned_data['TVL'], color=color, label='TVL')
    ax2.plot(aligned_data['date'], aligned_data['fees'], color='tab:green', label='Fees')
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  
    plt.legend()
    plt.show()

# Interpretation and Report
def interpret_results(correlation_results, aligned_data):
    report = f"Correlation Analysis Report\n"
    report += f"Sentiment vs TVL - Pearson: {correlation_results[0][0]}, Spearman: {correlation_results[1][0]}\n"
    report += f"Sentiment vs Fees - Pearson: {correlation_results[2][0]}, Spearman: {correlation_results[3][0]}\n"
    plot_data(aligned_data)
    return report

# Main Function
def main():
    sentiment_data = process_sentiment_data('sentiment_data.csv')
    financial_data = process_financial_data('financial_data.csv')
    aligned_data = align_data(sentiment_data, financial_data)
    correlation_results = calculate_correlation(aligned_data)
    report = interpret_results(correlation_results, aligned_data)
    print(report)

if __name__ == "__main__":
    main()
