import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io, base64

# --------------------------
# Q1: Which high court disposed the most cases from 2019–2022?
# --------------------------
def most_cases_disposed(df):
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    filtered = df[(df['year'] >= 2019) & (df['year'] <= 2022)]
    counts = filtered.groupby('court').size().reset_index(name='count')
    top_court = counts.sort_values('count', ascending=False).iloc[0]
    return top_court['court']

# --------------------------
# Q2: Regression slope of date_of_registration - decision_date by year for court=33_10
# --------------------------
def regression_slope_delay(df):
    court_df = df[df['court'] == '33_10'].copy()

    # Parse dates
    court_df['date_of_registration'] = pd.to_datetime(
        court_df['date_of_registration'], errors='coerce', dayfirst=True
    )
    court_df['decision_date'] = pd.to_datetime(
        court_df['decision_date'], errors='coerce', dayfirst=True
    )

    # Remove rows with missing dates
    court_df = court_df.dropna(subset=['date_of_registration', 'decision_date'])

    # Calculate delay in days
    court_df['delay_days'] = (
        court_df['decision_date'] - court_df['date_of_registration']
    ).dt.days

    # Group by year of decision_date and calculate mean delay
    yearly = (
        court_df.groupby(court_df['decision_date'].dt.year)['delay_days']
        .mean()
        .reset_index()
    )
    yearly.columns = ['year', 'avg_delay_days']

    # Fit linear regression
    slope, intercept = np.polyfit(yearly['year'], yearly['avg_delay_days'], 1)

    return slope, yearly

# --------------------------
# Q3: Plot year vs delay as base64 image
# --------------------------
def plot_delay_vs_year(yearly_df):
    plt.figure(figsize=(6, 4))
    plt.scatter(yearly_df['year'], yearly_df['avg_delay_days'], label="Average Delay")

    # Regression line
    slope, intercept = np.polyfit(yearly_df['year'], yearly_df['avg_delay_days'], 1)
    x_vals = np.linspace(yearly_df['year'].min(), yearly_df['year'].max(), 100)
    y_vals = slope * x_vals + intercept
    plt.plot(x_vals, y_vals, 'r-', label="Regression Line")

    plt.xlabel("Year")
    plt.ylabel("Average Delay (days)")
    plt.legend()
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

# --------------------------
# Entry point for direct execution (runs Q2)
# --------------------------
if __name__ == "__main__":
    # Example dataset for testing Q2
    data = [
        ["33_10", "01-01-2019", "10-01-2019", 2019],
        ["33_10", "05-02-2020", "20-02-2020", 2020],
        ["33_10", "01-03-2021", "10-03-2021", 2021],
        ["33_10", "05-04-2022", "25-04-2022", 2022],
    ]
    df_test = pd.DataFrame(data, columns=["court", "date_of_registration", "decision_date", "year"])

    slope, yearly_df = regression_slope_delay(df_test)
    print(f"Regression slope for Q2: {slope}")
    print("Yearly average delays:")
    print(yearly_df)
