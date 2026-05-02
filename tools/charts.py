import yfinance as yf
import matplotlib.pyplot as plt
import io
from PIL import Image

def generate_chart(symbol, period='1mo', interval='1d', target_trading_days=None):
    try:
        ticker = yf.Ticker(symbol)
        # Validate interval/period
        interval_limits = {'1m': '7d', '2m': '60d', '5m': '60d', '15m': '60d', '30m': '60d', '60m': '730d', '1h': '730d', '1d': 'max'}
        if period > interval_limits.get(interval, 'max'):
            period = interval_limits[interval]
        max_period = '60d' if interval != '1d' else '2y'
        data = ticker.history(period=max_period, interval=interval)
        if data.empty:
            fallback_int = {'10m':'15m', '90m':'1h'}.get(interval, interval)
            if fallback_int != interval:
                data = ticker.history(period=max_period, interval=fallback_int)
            if data.empty:
                return None
            print(f"Fallback to {fallback_int} for {symbol}")
        
        import pytz
        import matplotlib.dates as mdates
        ist_tz = pytz.timezone('Asia/Kolkata')
        if data.index.tz is None:
            data.index = data.index.tz_localize('UTC').tz_convert(ist_tz)
        else:
            data.index = data.index.tz_convert(ist_tz)

        # Strict NSE Trading Hours: Mon-Fri 09:15-15:30 IST
        trading_data = data[
            (data.index.weekday < 5) &  # Mon-Fri
            (
                ((data.index.hour > 9) | ((data.index.hour == 9) & (data.index.minute >= 15))) &
                ((data.index.hour < 15) | ((data.index.hour == 15) & (data.index.minute <= 30)))
            )
        ]
        if target_trading_days:
            # Get last N unique trading days
            trading_days = trading_data.index.normalize().unique()[-target_trading_days:]
            trading_data = trading_data[trading_data.index.normalize().isin(trading_days)]
        if trading_data.empty:
            trading_data = data
            print(f"Warning: No trading hours data for {symbol}, using full")

        import mplfinance as mpf
        mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc)
        fig, axlist = mpf.plot(trading_data, 
                               type='candle',
                               style=s,
                               volume=False,
                               title=f'{symbol} {period.upper()} ({interval}) - Trading Hours IST',
                               ylabel='Price (₹)',
                               figsize=(14,8),
                               returnfig=True,
                               datetime_format='%d-%m %H:%M' if interval in ['1m','5m','15m','30m','60m','1h'] else '%d-%m-%Y')
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
        img_buffer.seek(0)
        plt.close('all')
        
        return img_buffer
    except:
        return None
