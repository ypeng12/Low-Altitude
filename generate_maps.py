import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set publication style for matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

def generate_visualizations():
    input_file = "tripadvisor_level2_features.csv"
    if not os.path.exists(input_file):
        print(f"Error: {input_file} does not exist yet!")
        return

    print(f"Loading {input_file}...")
    df = pd.read_csv(input_file)
    print(f"Data loaded: {len(df)} rows.")

    # ----------------------------------------------------
    # 1. World Map Review Distribution (Plotly Choropleth)
    # ----------------------------------------------------
    try:
        import plotly.express as px
        import plotly.io as pio

        country_counts = df[df['user_country'] != 'Unknown']['user_country'].value_counts().reset_index()
        country_counts.columns = ['user_country', 'count']
        country_counts['log_count'] = np.log10(country_counts['count'])

        print("Generating World Map Choropleth...")
        fig_world = px.choropleth(
            country_counts,
            locations="user_country",
            locationmode="country names",
            color="count",
            hover_name="user_country",
            hover_data=["count"],
            color_continuous_scale="Greens",
            title="Figure 1: Global Distribution of TripAdvisor Low-Altitude Sightseeing Reviews",
            labels={'count': 'Number of Reviews'}
        )
        fig_world.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="DarkGray",
                projection_type='equirectangular',
                bgcolor='rgba(255,255,255,1)'
            ),
            font=dict(family="Arial, sans-serif", size=13),
            margin={"r":10,"t":50,"l":10,"b":10},
            coloraxis_colorbar=dict(
                title="Number of Reviews",
                thicknessmode="pixels", thickness=18,
                lenmode="pixels", len=300
            )
        )
        world_map_path = "world_map_reviews.png"
        fig_world.write_image(world_map_path, width=1200, height=650, scale=2)
        print(f"Saved {world_map_path}")

        # ----------------------------------------------------
        # 2. US State Review Distribution (Plotly Choropleth)
        # ----------------------------------------------------
        state_counts = df[df['is_us_domestic'] == 1]['user_state'].value_counts().reset_index()
        state_counts.columns = ['user_state', 'count']

        print("Generating US State Map Choropleth...")
        fig_us = px.choropleth(
            state_counts,
            locations="user_state",
            locationmode="USA-states",
            color="count",
            hover_name="user_state",
            hover_data=["count"],
            scope="usa",
            color_continuous_scale="Greens",
            title="Figure 2: US Domestic Tourist Origin State Distribution",
            labels={'count': 'Number of Reviews'}
        )
        fig_us.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                bgcolor='rgba(255,255,255,1)'
            ),
            font=dict(family="Arial, sans-serif", size=13),
            margin={"r":10,"t":50,"l":10,"b":10},
            coloraxis_colorbar=dict(
                title="Number of Reviews",
                thicknessmode="pixels", thickness=18,
                lenmode="pixels", len=300
            )
        )
        us_map_path = "us_map_reviews.png"
        fig_us.write_image(us_map_path, width=1100, height=650, scale=2)
        print(f"Saved {us_map_path}")

    except Exception as e:
        print(f"Plotly map generation notice: {e}")

    # ----------------------------------------------------
    # 3. Low-Altitude Feature Mention Rate Bar Chart (Matplotlib/Seaborn)
    # ----------------------------------------------------
    print("Generating Feature Distribution Summary Plot...")
    feature_labels = {
        'pilot_service_mention': 'Pilot & Crew Interaction',
        'coast_mention': 'Coast & Ocean Scenery',
        'canyon_mention': 'Canyon & Valley Views',
        'waterfall_mention': 'Waterfall Mentions',
        'weather_mention': 'Weather & Visibility',
        'price_value_mention': 'Price & Value Perception',
        'safety_mention': 'Safety & Anxiety Perception',
        'special_occasion': 'Special Travel Occasion',
        'helicopter_comparison': 'Helicopter vs Plane Comparison',
        'wildlife_mention': 'Wildlife Sightings (Whales)'
    }

    feature_cols = list(feature_labels.keys())
    rates = df[feature_cols].mean() * 100
    summary_df = pd.DataFrame({
        'Feature': [feature_labels[c] for c in feature_cols],
        'Percentage': rates.values
    }).sort_values(by='Percentage', ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    bars = ax.barh(summary_df['Feature'], summary_df['Percentage'], color='#2E8B57', edgecolor='#1C5434', height=0.65)

    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{width:.1f}%',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0),
                    textcoords="offset points",
                    ha='left', va='center', fontsize=10, fontweight='bold', color='#1C5434')

    ax.set_title("Prevalence of Low-Altitude Experience Attributes in Reviews (%)", fontsize=14, pad=15, fontweight='bold')
    ax.set_xlabel("Percentage of Reviews Containing Attribute (%)", fontsize=11)
    ax.set_xlim(0, max(summary_df['Percentage']) * 1.15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()

    feature_plot_path = "low_altitude_feature_distribution.png"
    plt.savefig(feature_plot_path, dpi=300)
    plt.close()
    print(f"Saved {feature_plot_path}")

    # Export Top Countries and States CSV summary for paper tables
    summary_country = df['user_country'].value_counts().head(15).reset_index()
    summary_country.columns = ['Country', 'Review_Count']
    summary_country['Percentage (%)'] = (summary_country['Review_Count'] / len(df) * 100).round(2)
    summary_country.to_csv("paper_table_country_distribution.csv", index=False)

    summary_state = df[df['is_us_domestic']==1]['user_state'].value_counts().head(15).reset_index()
    summary_state.columns = ['US_State', 'Review_Count']
    summary_state['Percentage_of_US (%)'] = (summary_state['Review_Count'] / df['is_us_domestic'].sum() * 100).round(2)
    summary_state.to_csv("paper_table_us_state_distribution.csv", index=False)
    print("Exported paper summary tables!")

if __name__ == "__main__":
    generate_visualizations()
