import numpy as np
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import style
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets
style.use('dark_background')

class StockChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#1e222a')
        self.axes = self.fig.add_subplot(111)
        super(StockChart, self).__init__(self.fig)
        self.setParent(parent)
        
        
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, 
                          QtWidgets.QSizePolicy.Policy.Expanding)
        self.updateGeometry()
        
        
        self.price_tracker = None
        self.mpl_connect('motion_notify_event', self.on_mouse_move)
        
    def plot_stock_data(self, prices, dates, symbol, currency="₹"):
        self.axes.clear()
        x = np.arange(len(prices))
        self.prices = prices
        self.dates = dates
        self.currency = currency
        
        if isinstance(dates[0], datetime) and isinstance(dates[-1], datetime):
            self.date_range = (dates[-1] - dates[0]).days
        else:
            try:
                first_date = datetime.strptime(str(dates[0]).split("+")[0].strip(), '%Y-%m-%d %H:%M:%S') if "+" in str(dates[0]) else datetime.strptime(str(dates[0]), '%Y-%m-%d')
                last_date = datetime.strptime(str(dates[-1]).split("+")[0].strip(), '%Y-%m-%d %H:%M:%S') if "+" in str(dates[-1]) else datetime.strptime(str(dates[-1]), '%Y-%m-%d')
                self.date_range = (last_date - first_date).days
            except:
                self.date_range = len(dates)
        
        
        if prices[-1] >= prices[0]:
            line_color = '#00c853'
            fill_color = '#00c85320'
            accent_color = '#00952d'
        else:
            line_color = '#ff5252'
            fill_color = '#ff525220'
            accent_color = '#c50e29'
        
        self.axes.plot(x, prices, linewidth=2.5, color=line_color, zorder=3)
        self.axes.fill_between(x, prices, min(prices), alpha=0.3, color=fill_color, zorder=2)
        
        self.axes.grid(True, linestyle='--', alpha=0.2, color='#e0e0e0', zorder=1)
        self.axes.set_facecolor('#2a2e39')
        
        
        if isinstance(dates[0], datetime) and isinstance(dates[-1], datetime):
            date_range = (dates[-1] - dates[0]).days
        else:
            date_range = len(dates)
        
        if date_range > 365:
            num_ticks = 6
        elif date_range > 180:
            num_ticks = 5
        elif date_range > 90:
            num_ticks = 4
        elif date_range > 30:
            num_ticks = 5
        else:
            num_ticks = 6
            
        tick_indices = []
        for i in range(num_ticks):
            idx = int(i * (len(prices)-1) / (num_ticks-1))
            tick_indices.append(idx)
        
        self.axes.set_xticks(tick_indices)
        
        date_labels = []
        for idx in tick_indices:
            if idx < len(dates):
                date_obj = dates[idx]
                if isinstance(date_obj, str):
                    try:
                        # Handle ISO format dates with timezone
                        if "+" in date_obj:
                            date_parts = date_obj.split("+")[0].strip()
                            date_obj = datetime.strptime(date_parts, '%Y-%m-%d %H:%M:%S')
                        else:
                            date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
                    except:
                        pass
                
                if isinstance(date_obj, datetime):
                    if date_range > 365:
                        date_labels.append(date_obj.strftime('%b\n%Y'))
                    elif date_range > 90:
                        date_labels.append(date_obj.strftime('%b\n%d'))
                    elif date_range > 30:
                        date_labels.append(date_obj.strftime('%b %d'))
                    else:
                        # For intraday data
                        if date_obj.hour == 0 and date_obj.minute == 0:
                            date_labels.append(date_obj.strftime('%b %d'))
                        else:
                            date_labels.append(date_obj.strftime('%I:%M\n%p'))
                else:
                    date_labels.append(str(date_obj))
            else:
                date_labels.append("")
        
        # Set tick labels
        self.axes.set_xticklabels(date_labels, color='#e0e0e0', rotation=0, fontsize=9)
        self.axes.tick_params(axis='x', pad=8)
        self.axes.tick_params(axis='y', colors='#e0e0e0', labelsize=9)
        
        if date_range > 365:
            # For yearly view
            self.fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
        elif date_range > 180:
            # For 6 month view
            self.fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
        elif date_range > 30:
            # For 1-6 month view
            self.fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.12)
        else:
            # For < 1 month view
            self.fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)
        
       
        y_min, y_max = min(prices), max(prices)
        y_padding = (y_max - y_min) * 0.05
        self.axes.set_ylim(y_min - y_padding, y_max + y_padding)
        
        self.axes.set_title(f"{symbol} Price History", 
                          fontweight='bold', color='#e0e0e0', 
                          fontsize=12, pad=10)
        
        if prices[-1] > prices[0]:
            trend_color = '#4caf50'
            trend_text = "▲"
            change_pct = ((prices[-1] - prices[0]) / prices[0]) * 100
            trend_label = f"+{change_pct:.2f}%"
        else:
            trend_color = '#f44336'
            trend_text = "▼"
            change_pct = ((prices[0] - prices[-1]) / prices[0]) * 100
            trend_label = f"-{change_pct:.2f}%"
            
        start_date = dates[0]
        end_date = dates[-1]
        if isinstance(start_date, str):
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except:
                pass
        if isinstance(end_date, str):
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            except:
                pass
        
        # Choose date format based on range
        if date_range > 365:
            start_date_str = start_date.strftime('%b %Y') if isinstance(start_date, datetime) else str(start_date)
            end_date_str = end_date.strftime('%b %Y') if isinstance(end_date, datetime) else str(end_date)
        else:
            start_date_str = start_date.strftime('%b %d') if isinstance(start_date, datetime) else str(start_date)
            end_date_str = end_date.strftime('%b %d') if isinstance(end_date, datetime) else str(end_date)
            
        
        self.axes.plot(0, prices[0], 'o', markersize=5, color=accent_color, zorder=4)
        self.axes.plot(len(prices)-1, prices[-1], 'o', markersize=5, color=accent_color, zorder=4)
        
       
        self.axes.text(0.03, 0.97, 
                     f"{trend_text} {trend_label}",
                     transform=self.axes.transAxes,
                     fontsize=10, color=trend_color, fontweight='bold',
                     verticalalignment='top', horizontalalignment='left',
                     bbox=dict(boxstyle="round,pad=0.3", fc='#2a2e39', ec=trend_color, alpha=0.7))
        
        self.axes.text(0.97, 0.97, 
                     f"High: {currency}{max(prices):.2f}\nLow: {currency}{min(prices):.2f}",
                     transform=self.axes.transAxes,
                     fontsize=9, color='#e0e0e0',
                     verticalalignment='top', horizontalalignment='right',
                     bbox=dict(boxstyle="round,pad=0.3", fc='#2a2e39', ec='#616161', alpha=0.7))
        
        
        for spine in self.axes.spines.values():
            spine.set_visible(False)
        
        self.price_tracker = self.axes.axvline(x=0, color='#bbbbbb', linestyle='--', alpha=0, lw=1)
        self.price_label = self.axes.text(0, 0, "", 
                                        bbox=dict(boxstyle="round,pad=0.3", fc='#2a2e39', ec="gray", alpha=0.9),
                                        color='#e0e0e0', fontsize=9, ha='center')
        self.price_label.set_visible(False)
        
        
        self.draw()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fig.tight_layout(pad=2.0)
        self.draw_idle()
        
    def on_mouse_move(self, event):
        if (event.inaxes != self.axes or not hasattr(self, 'prices') or 
            not hasattr(self, 'dates') or self.price_tracker is None):
            if self.price_tracker and self.price_tracker.get_alpha() > 0:
                self.price_tracker.set_alpha(0)
                self.price_label.set_visible(False)
                self.draw_idle()
            return
        
        x_val = int(round(event.xdata))
        if x_val < 0 or x_val >= len(self.prices):
            return
            
        self.price_tracker.set_xdata([x_val, x_val])
        self.price_tracker.set_alpha(0.4)
        
        price = self.prices[x_val]
        
        date = self.dates[x_val]
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, '%Y-%m-%d')
            except:
                # Try to handle other date formats
                try:
                    # If the date includes time information
                    if "+" in date:
                        # Split at the plus sign and only use the first part
                        date_parts = date.split("+")[0].strip()
                        date = datetime.strptime(date_parts, '%Y-%m-%d %H:%M:%S')
                    else:
                        # Try a generic format
                        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                except:
                    # Keep as string if parsing fails
                    pass
        
        # Format the date string in a more readable way
        if isinstance(date, datetime):
            # Different formats based on the data frequency
            if hasattr(self, 'date_range') and self.date_range > 365:
                # For yearly data
                date_str = date.strftime('%b %d, %Y')
            elif hasattr(self, 'date_range') and self.date_range > 30:
                # For monthly data
                date_str = date.strftime('%b %d, %Y')
            else:
                # For daily or intraday data
                if date.hour == 0 and date.minute == 0:
                    # Just a date
                    date_str = date.strftime('%b %d, %Y')
                else:
                    # Date with time
                    date_str = date.strftime('%b %d, %Y %I:%M %p')
        else:
            date_str = str(date)
        
        self.price_label.set_text(f"{date_str}\n{self.currency}{price:.2f}")
        
        x_pos = x_val
        y_pos = price
        x_bounds = self.axes.get_xlim()
        width = x_bounds[1] - x_bounds[0]
        
        if x_val < width * 0.1:
            self.price_label.set_horizontalalignment('left')
        elif x_val > width * 0.9:
            self.price_label.set_horizontalalignment('right')
        else:
            self.price_label.set_horizontalalignment('center')
            
        self.price_label.set_position((x_pos, y_pos))
        self.price_label.set_visible(True)
        
        self.draw_idle()