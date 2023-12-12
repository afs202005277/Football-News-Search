import matplotlib.pyplot as plt
import numpy as np
import excel_analysis


def plot_relevance(data):
    schemas = list(data.keys())
    queries = list(data[schemas[0]].keys())
    num_schemas = len(schemas)

    bar_width = 0.2
    index = np.arange(len(queries))

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, schema in enumerate(schemas):
        r_counts = []
        n_counts = []

        for query in queries:
            relevances = data[schema][query]
            r_count = relevances.count("R")
            n_count = relevances.count("N")
            r_counts.append(r_count)
            n_counts.append(n_count)

        bar_positions_r = index + i * (bar_width + 0.01)
        bar_positions_n = index + i * (bar_width + 0.01)

        ax.bar(bar_positions_r, r_counts, bar_width, color='green', label=f'{schema} (R)')
        ax.bar(bar_positions_n, n_counts, bar_width, color='red', bottom=r_counts, label=f'{schema} (N)')

    ax.set_xlabel('Queries')
    ax.set_ylabel('Relevance Counts')
    ax.set_xticks(index + (bar_width * (num_schemas - 1) / 2))
    ax.set_xticklabels(queries)
    ax.legend()

    plt.show()


# Call the function with your data
plot_relevance(excel_analysis.get_relevance_analysis()

input_data = {
    'Schema1': {
        'Query1': 'RNRN',
        'Query2': 'RNNR',
        'Query3': 'RRRN'
    },
    'Schema2': {
        'Query1': 'RN',
        'Query2': 'NNR',
        'Query3': 'RNR'
    },
    # Add more schemas and queries as needed
}
