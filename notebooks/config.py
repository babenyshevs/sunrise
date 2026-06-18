# Shared plotting and labeling configuration for all notebooks.

BOOSTER_LABEL_MAP = {0: "No Booster", 1: "Has Booster"}

# Consistent colors for treatment groups across notebooks.
BOOSTER_COLORS = {
    "No Booster": "#B8B1AC",
    "Has Booster": "#E85C2A",
}

# Ordered list form of BOOSTER_COLORS for matplotlib/pandas .plot() calls
# (which require positional color lists rather than hue-keyed dicts).
BOOSTER_COLOR_LIST = [BOOSTER_COLORS["No Booster"], BOOSTER_COLORS["Has Booster"]]

# Churn-status palette for charts that split by churn outcomes.
CHURN_STATUS_COLORS = {
    "Not Canceled": "#6B625D",
    "Canceled": "#D72638",
}

# Financial chart colors.
FINANCIAL_COLORS = {
    "cost": "#B8B1AC",
    "saved": "#E85C2A",
    "net_positive": "#F59E0B",
    "net_negative": "#C62828",
    "reference": "#4A4543",
}

# Shared matplotlib theme for charts.
MATPLOTLIB_THEME = {
    "axes.edgecolor": "#D8D3CF",
    "axes.labelcolor": "#4A4543",
    "axes.titlecolor": "#2F2B29",
    "xtick.color": "#6B625D",
    "ytick.color": "#6B625D",
    "grid.color": "#ECE7E2",
    "grid.alpha": 1.0,
    "axes.facecolor": "#FFFFFF",
    "figure.facecolor": "#FFFFFF",
}

# Seaborn theme defaults.
SNS_STYLE = "whitegrid"
SNS_PALETTE = "muted"

# Shared figure height for all notebook plots.
FIGURE_HEIGHT = 5

# Bar edge colour applied to all bar/stacked charts.
BAR_EDGE_COLOR = "white"

# Colormap names.
HEATMAP_CMAP = "YlOrRd"        # TV × Mobile bundle heatmap (Plot 4)
CORRELATION_CMAP = "RdBu_r"    # Mixed-method correlation matrix (Plot 7)
AGE_GROUP_PALETTE = "Blues_d"  # Age-group churn bar chart (Plot 8)

# Tenure life-stage curve colors (Plot 5).
TENURE_COHORT_COLORS = {
    "bar":       "#c8d9e8",   # background volume bars
    "line":      "#e87040",   # churn-rate line + markers
    "bar_axis":  "#7fb3d3",   # customer-count axis label
    "line_axis": "#e87040",   # churn-rate axis label
}

# Regional churn bar colors (Plot 9).
CHURN_RATE_COLORS = {
    "above_avg": "#e87040",  # bars above the overall average
    "below_avg": "#7fb3d3",  # bars below the overall average
    "reference": "black",    # overall-average reference line
}

# Font sizes.
FONT_SIZE_TITLE    = 13  # main plot title / suptitle
FONT_SIZE_SUBTITLE = 12  # secondary or long multi-line titles
FONT_SIZE_LABEL    = 9   # small bar-labels and annotation callouts
FONT_SIZE_LABEL_MD = 10  # medium bar-labels and annotation callouts

# Font colors.
FONT_COLOR_ON_BAR     = "white"   # text rendered inside / on colored bars
FONT_COLOR_ANNOTATION = "black"   # standard annotation and axis-label text