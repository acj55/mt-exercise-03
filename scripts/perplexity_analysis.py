
""" MT ex03 Task 2: validation perplexity extraction and analysis """

import re
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# model names and log paths
logs = {
    "Baseline": "models/deen_transformer_pre/baseline.log",
    "Prenorm": "models/pre_LN/train.log",
    "Postnorm": "models/post_LN/train.log",
}

def extract_validation_ppl(log_file):
    text = Path(log_file).read_text(errors="replace")

    rows = []
    last_step = None

    for line in text.splitlines():
        step_match = re.search(r"Step:\s*(\d+)", line)
        if step_match:
            last_step = int(step_match.group(1))

        ppl_match = re.search(r"Evaluation result.*?ppl:\s*([0-9.]+)", line)
        if ppl_match and last_step is not None:
            rows.append((last_step, float(ppl_match.group(1))))

    return pd.DataFrame(rows, columns=["Validation ppl", "ppl"])


dfs = []

for model, file in logs.items():
    df = extract_validation_ppl(file)
    df = df.rename(columns={"ppl": model})
    dfs.append(df)

table = dfs[0]
for df in dfs[1:]:
    table = table.merge(df, on="Validation ppl", how="outer")

table = table.sort_values("Validation ppl")

table.to_csv("ppl_data/validation_perplexities.csv", index=False)
print(table)

# line plot
plt.figure(figsize=(10, 6))

for model in logs.keys():
    plt.plot(
        table["Validation ppl"],
        table[model],
        marker="o",
        label=model
    )

plt.xlabel("Training step")
plt.ylabel("Validation perplexity")
plt.title("Validation perplexity during training")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("ppl_data/validation_perplexities.png", dpi=300)
plt.show()