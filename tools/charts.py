import yfinance as yf
import matplotlib.pyplot as plt
import io
from PIL import Image

def generate_chart(symbol, period='1mo', interval='1d'):
    try:
        ticker = yf.Ticker(symbol)
        # Validate interval/period
        interval_limits = {'1m': '7d', '2m': '60d', '5m': '60d', '15m': '60d', '30m': '60d', '60m': '730d', '1h': '730d', '1d': 'max'}
        if period > interval_limits.get(interval, 'max'):
            period = interval_limits[interval]
        data = ticker.history(period=period, interval=interval)
        if data.empty:
            return None
        
        import pytz
        import matplotlib.dates as mdates
        ist_tz = pytz.timezone('Asia/Kolkata')
        data.index = data.index.tz_convert(ist_tz)
        plt.figure(figsize=(12, 6))
        if len(data) > 300:
            step = max(1, len(data) // 200)
            data_plot = data.iloc[::step]
        else:
            data_plot = data
        plt.plot(data_plot.index, data_plot['Close'], label='Close', linewidth=1.5)
        plt.title(f'{symbol} {period.upper()} ({interval}) - IST')
        plt.xlabel('Date / Time (IST)')
        plt.ylabel('Price (₹)')
        plt.legend()
        plt.xticks(rotation=45)
        if interval in ['1m', '5m', '15m', '30m', '60m', '1h']:
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%M IST'))
            plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=4))
        else:
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y IST'))
        fig = plt.gcf()
        fig.autofmt_xdate()
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    except:
        return None
