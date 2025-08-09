import base64
from io import BytesIO
import matplotlib.pyplot as plt

def image_to_base64_uri(fig: plt.Figure) -> str:
    """
    Encodes a matplotlib figure to a base64 data URI string.
    Ensures the figure is closed after saving to free up memory.
    """
    buf = BytesIO()
    try:
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"
    finally:
        plt.close(fig) # Close the figure to prevent memory leaks