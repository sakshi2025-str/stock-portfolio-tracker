import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import yfinance as yf
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class Portfolio:
    def __init__(self):
        self.stocks = {}

    def add_stock(self, symbol, quantity):
        stock_data = get_stock_data(symbol)
        latest_data = stock_data.iloc[-1]
        closing_price = latest_data['Close']

        if symbol in self.stocks:
            self.stocks[symbol]['quantity'] += quantity
        else:
            self.stocks[symbol] = {'quantity': quantity, 'latest_price': closing_price, 'history': stock_data}

    def calculate_total_value(self):
        total_value = sum(stock['quantity'] * stock['latest_price'] for stock in self.stocks.values())
        return total_value

    def calculate_portfolio_allocation(self):
        total_value = self.calculate_total_value()
        allocations = {symbol: (stock['quantity'] * stock['latest_price']) / total_value for symbol, stock in self.stocks.items()}
        return allocations

def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        history = stock.history(period="1y")
        return history
    except Exception as e:
        messagebox.showerror('Data Error', f'Error fetching data for {symbol}: {e}')
        return None

def visualize_stock_data(event):
    for widget in bottom_frame.winfo_children():
        widget.destroy()

    cur_item = portfolio_display.focus()
    if cur_item and portfolio_display.item(cur_item)['values']:
        stock_symbol = portfolio_display.item(cur_item)['values'][0]
        stock_data = portfolio.stocks[stock_symbol]['history']

        fig = Figure(figsize=(8, 6), dpi=100)
        a = fig.add_subplot(111)
        a.plot(stock_data.index, stock_data['Close'], label='Close')
        a.set_xlabel('Date')
        a.set_ylabel('Price')
        a.set_title(f'{stock_symbol} Closing Price')

        canvas = FigureCanvasTkAgg(fig, master=bottom_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side='left', padx=10)

        info_frame = ttk.LabelFrame(bottom_frame, text='Analytics and Portfolio Diversification')
        info_frame.pack(side='left', padx=10)

        benchmark_data = get_stock_data('^GSPC')
        if benchmark_data is not None:
            returns = np.log(stock_data['Close'] / stock_data['Close'].shift(1))
            volatility = returns.std() * np.sqrt(252)
            annual_returns = np.exp(252 * returns.mean()) - 1
            benchmark_returns = np.log(benchmark_data['Close'] / benchmark_data['Close'].shift(1)).mean() * 252
            performance_against_benchmark = (1 + annual_returns) / (1 + benchmark_returns) - 1

            volatility_label = tk.Label(info_frame, text=f'Volatility: {volatility:.2f}', font='Helvetica 12 bold')
            volatility_label.pack(pady=5)

            returns_label = tk.Label(info_frame, text=f'Annual Returns: {annual_returns:.2f}', font='Helvetica 12 bold')
            returns_label.pack(pady=5)

            benchmark_label = tk.Label(info_frame, text=f'Performance against Benchmark (S&P500): {performance_against_benchmark:.2f}', font='Helvetica 12 bold')
            benchmark_label.pack(pady=5)

def draw_pie_chart(frame):
    for widget in frame.winfo_children():
        widget.destroy()
    allocations = portfolio.calculate_portfolio_allocation()

    fig_pie = Figure(figsize=(5, 5), dpi=100)
    ax_pie = fig_pie.add_subplot(111)
    labels = list(allocations.keys())
    sizes = list(allocations.values())
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6', '#c2f0c2', '#ffb3b3']
    ax_pie.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax_pie.axis('equal')
    ax_pie.set_title('Portfolio Total Value Diversification', fontdict={'fontsize': 10, 'fontweight': 'bold'})

    canvas_pie = FigureCanvasTkAgg(fig_pie, master=frame)
    canvas_pie.draw()
    canvas_pie.get_tk_widget().pack()

def add_stock_to_portfolio():
    stock_symbol = stock_symbol_entry.get()
    try:
        quantity = float(stock_quantity_entry.get())
        if stock_symbol == '' or quantity <= 0:
            raise ValueError("Invalid input")
    except ValueError:
        messagebox.showerror('Invalid Input', 'Please enter a valid stock symbol and quantity.')
        return

    portfolio.add_stock(stock_symbol, quantity)

    total_value = portfolio.calculate_total_value()
    total_portfolio_value_label['text'] = f'Total Portfolio Value: ${total_value:,.2f}'

    for i in portfolio_display.get_children():
        portfolio_display.delete(i)
    for symbol, info in portfolio.stocks.items():
        stock_value = info['quantity'] * info['latest_price']
        portfolio_display.insert('', 'end', values=(symbol, info['quantity'], f'${stock_value:,.2f}'))
    
    draw_pie_chart(pie_frame)

if __name__ == '__main__':
    portfolio = Portfolio()

    root = tk.Tk()
    root.title('Stock Portfolio Tracker')

    top_frame = tk.Frame(root)
    top_frame.pack()

    stock_symbol_label = tk.Label(top_frame, text='Enter Stock Ticker:', font='Helvetica 12 bold')
    stock_symbol_label.pack(side='left')
    stock_symbol_entry = tk.Entry(top_frame, font='Helvetica 12')
    stock_symbol_entry.pack(side='left')

    stock_quantity_label = tk.Label(top_frame, text='Enter Quantity:', font='Helvetica 12 bold')
    stock_quantity_label.pack(side='left')
    stock_quantity_entry = tk.Entry(top_frame, font='Helvetica 12')
    stock_quantity_entry.pack(side='left')

    add_stock_button = tk.Button(top_frame, text='Add Stock', command=add_stock_to_portfolio, font='Helvetica 12')
    add_stock_button.pack(side='left')

    total_portfolio_value_label = tk.Label(top_frame, text='Total Portfolio Value: $0.00', font='Helvetica 14 bold')
    total_portfolio_value_label.pack(side='left')

    middle_frame = tk.Frame(root)
    middle_frame.pack()

    portfolio_display = ttk.Treeview(middle_frame, columns=('Ticker', 'Quantity', 'Total Stock Value'), show='headings')
    portfolio_display.heading('Ticker', text='Ticker', anchor='center')
    portfolio_display.heading('Quantity', text='Quantity', anchor='center')
    portfolio_display.heading('Total Stock Value', text='Total Stock Value', anchor='center')
    portfolio_display.column('Ticker', width=100, anchor='center')
    portfolio_display.column('Quantity', width=100, anchor='center')
    portfolio_display.column('Total Stock Value', width=150, anchor='center')
    portfolio_display.pack(side='left')

    portfolio_display.bind('<<TreeviewSelect>>', visualize_stock_data)

    pie_frame = tk.Frame(middle_frame)
    pie_frame.pack(side='left', padx=10)

    bottom_frame = tk.Frame(root)
    bottom_frame.pack()

    root.mainloop()