import matplotlib.pyplot as plt
from io import BytesIO
import re

def extract_chart_data(response: str) -> dict:
    import re

    data = {}
    pattern = r"(FY\d{2}|\d{4}).*?(INR|\$)?\s?([\d,]+\.?\d*)\s?(Million|Billion)?"
    matches = re.findall(pattern, response)

    for label, currency, amount_str, scale in matches:
        if not amount_str.strip():
            continue  

        try:
            amount = float(amount_str.replace(",", ""))
        except ValueError:
            continue  

        if scale == "Million":
            amount *= 1_000_000
        elif scale == "Billion":
            amount *= 1_000_000_000

        data[label] = amount

    return data


def generate_revenue_chart(data: dict) -> BytesIO:
    fig, ax = plt.subplots()
    ax.bar(data.keys(), data.values(), color=["#888", "#1f77b4"])
    ax.set_title("Revenue Growth")
    ax.set_ylabel("Billions USD")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf
