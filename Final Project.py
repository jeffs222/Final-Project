import tkinter as tk
from tkinter import StringVar, messagebox
from tkinter.scrolledtext import ScrolledText
import google.generativeai as genai
import yfinance as yf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# this is to draw/plot the graph

# canvas for the graph/plotting
graph_canva = None
# creation of window
main_window = tk.Tk()
main_window.geometry('1400x750')
main_window.title('Ticker getter')

ticker = StringVar()
ticker.set('AAPL')
get_info_flag = tk.BooleanVar(
    value=False)  # for the get info button to be clicked, such trigger will be noticed by grpah
start_date = tk.StringVar()
start_date.set(' ')
end_date = tk.StringVar()
end_date.set(' ')

# intervals variable CONSTANT
DAY1 = '1D'
DAY5 = '5D'
MONTH1 = '1M'
YEAR1 = '1Y'
interval_variable = tk.StringVar(value=MONTH1)

user_api_key = ''

if user_api_key == '':
    messagebox.showerror('Error', 'Please enter your API key')
    main_window.destroy()
elif 'AIza' not in user_api_key:
    messagebox.showerror("Invalid API Key", "This does not look like a valid Google Gemini API key.")
    main_window.destroy()
else:
    genai.configure(api_key=user_api_key)

model = genai.GenerativeModel("gemini-2.5-flash")


# Function for the ai comment
def ai_comment_on_stock(hist, ticker_symbol):
    try:
        stock_desc_label.config(text='AI comment loading…')
        main_window.update()

        close_prices = hist['Close'].values.tolist()

        data_summary = (
            f'The stock {ticker_symbol} has {len(close_prices)} data points. '
            f'The first closing price was {close_prices[0]:.2f} and the last was {close_prices[-1]:.2f}.'
        )

        prompt = (
            'You are a really nice financial analyst explaining the stock trends using simple terms.\n'
            f'Based on this data summary, write 2–3 sentences describing the overall trend and add any helpful insight:\n\n{data_summary}'
            f' And give a good advice when it comes to buying or not buying the stock'
        )

        response = model.generate_content(prompt)
        ai_comment = response.text.strip()
        return ai_comment

    except Exception as e:
        return f'AI comment not available : {e}'

    # ticker information


def get_ticker():
    try:
        stock = yf.Ticker(ticker.get())
        info = stock.info
        current_price = info.get('currentPrice')
        previous_close = info.get('previousClose')

        if current_price is None or previous_close is None:
            raise ValueError("Price data unavailable")

        percent_change = f'{((current_price - previous_close) / previous_close) * 100:.2f}%'

        cur_price.set(f'${current_price:.2f}')
        prev_price.set(f'${previous_close:.2f}')
        percent_var.set(percent_change)
    except Exception:
        messagebox.showerror('Error', f'Unable to retrieve data for {ticker.get()}')
        return


def get_info_flag_clicked():
    get_info_flag.set(True)
    get_ticker()
    plot_graph()


# plot graph
def plot_graph(interval='1d', period='1mo'):
    global graph_canva

    if not get_info_flag.get():
        messagebox.showerror('Error', f'Get Info button isn’t enabled or Ticker isn’t connected')
        return

    try:
        tk_obj = yf.Ticker(ticker.get())
        hist = tk_obj.history(interval=interval, period=period)
        if hist.empty:
            messagebox.showerror('Error', f'Unable to retrieve data for {ticker.get()}')
            return

            # clear previous graph
        if graph_canva is not None:
            graph_canva.get_tk_widget().destroy()
            graph_canva = None

        fig = Figure(figsize=(6, 4), dpi=90)  # smaller graph footprint
        ax = fig.add_subplot(111)
        ax.plot(hist.index, hist['Close'])
        ax.set_title(f'{ticker.get()} History ({period}/{interval})', fontsize=10)
        ax.set_xlabel('Date', fontsize=9)
        ax.set_ylabel('Close Price', fontsize=9)
        ax.tick_params(axis='both', labelsize=8)
        ax.grid(True, alpha=0.5)

        draw = FigureCanvasTkAgg(fig, master=graph_frame)
        draw.draw()
        draw.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        graph_canva = draw

        # Ai comment for when the graph changes
        ai_comment = ai_comment_on_stock(hist, ticker.get())
        stock_desc_label.config(text=f"AI Comment: {ai_comment}")

    except Exception as e:
        messagebox.showerror('Error', f'Failure to retrieve data or draw graph: {e}')
        return

    # switching the interval


def change_interval():
    if not get_info_flag.get():
        messagebox.showerror('Error', f'Get Info button is disabled')
        return
    else:
        selection = interval_variable.get()
        if selection == '1D':
            interval, period = "5m", "1d"
        elif selection == '5D':
            interval, period = "30m", "5d"
        elif selection == '1Y':
            interval, period = "1wk", "1y"
        else:
            interval, period = "1d", "1mo"

    plot_graph(interval=interval, period=period)


def quit_btn():
    main_window.destroy()


# GUI layout
header_frame = tk.Frame(main_window, bg='black', height=36)  # smaller height
header_frame.pack(side='top', fill='x')
header_title = tk.Label(header_frame, text='Stock App', font=('arial', 14, 'bold'), bg='black',
                        fg='white')  # smaller font
header_title.pack(side='left', fill='x', padx=10, pady=6)

main_frame = tk.Frame(main_window, bg='white', highlightthickness=1, highlightbackground='light gray')
main_frame.pack(side='left', fill='both', expand=True, padx=6, pady=6)  # tighter padding
main_frame.grid_columnconfigure(0, weight=1)

inside_frame = tk.Frame(main_frame, bg='white')
inside_frame.grid(row=0, column=0, padx=6, pady=6, sticky='ew')

info_label = tk.Label(inside_frame, text='Enter ticker', font=('arial', 10, 'bold'), fg='black',
                      bg='white')  # smaller label
info_label.grid(row=0, column=0, padx=(0, 6), pady=4, sticky='w')
ticker_entry = tk.Entry(inside_frame, textvariable=ticker, width=12)  # narrower entry
ticker_entry.grid(row=0, column=1, padx=6, pady=4, sticky='w')

get_info_btn = tk.Button(
    inside_frame, text="Get Info", font=('arial', 10, 'bold'),  # smaller font
    fg='black', bg='blue', width=8, cursor='hand2', command=get_info_flag_clicked  # narrower
)
get_info_btn.grid(row=0, column=2, padx=6, pady=4, sticky='w')

boxes_container = tk.Frame(main_frame, bg='white')
boxes_container.grid(row=1, column=0, padx=6, pady=6, sticky='ew')
boxes_container.grid_columnconfigure(0, weight=1)
boxes_container.grid_columnconfigure(1, weight=1)
boxes_container.grid_columnconfigure(2, weight=1)

cur_price = tk.StringVar(value="$0.00")
prev_price = tk.StringVar(value="$0.00")
percent_var = tk.StringVar(value="0.00%")

# current price card
tk.Label(boxes_container, text="Current Price", bg="white", fg="black", font=("arial", 9, "bold")).grid(row=0, column=0,
                                                                                                        padx=6,
                                                                                                        sticky="w")
tk.Label(boxes_container, textvariable=cur_price, bg="white", fg="black", font=("arial", 10, "bold")).grid(row=1,
                                                                                                           column=0,
                                                                                                           padx=6,
                                                                                                           sticky="w")

# previous close card
tk.Label(boxes_container, text="Previous Close", bg="white", fg="black", font=("arial", 9, "bold")).grid(row=0,
                                                                                                         column=1,
                                                                                                         padx=6,
                                                                                                         sticky="w")
tk.Label(boxes_container, textvariable=prev_price, bg="white", fg="black", font=("arial", 10, "bold")).grid(row=1,
                                                                                                            column=1,
                                                                                                            padx=6,
                                                                                                            sticky="w")

# percent change card
tk.Label(boxes_container, text="Percent Change", bg="white", fg="black", font=("arial", 9, "bold")).grid(row=0,
                                                                                                         column=2,
                                                                                                         padx=6,
                                                                                                         sticky="w")
tk.Label(boxes_container, textvariable=percent_var, bg="white", fg="black", font=("arial", 10, "bold")).grid(row=1,
                                                                                                             column=2,
                                                                                                             padx=6,
                                                                                                             sticky="w")

# graph area
graph_frame = tk.Frame(main_frame, bg='white')
graph_frame.grid(row=2, column=0, padx=6, pady=6, sticky='ew')
graph_frame.grid_columnconfigure(0, weight=1)
graph_frame.grid_rowconfigure(0, weight=1)

# AI description label
stock_desc_label = tk.Label(main_frame, text="", bg='white', fg='black',
                            font=('arial', 12, 'italic'), wraplength=1200, justify='left')  # smaller font and wrap
stock_desc_label.grid(row=4, column=0, padx=6, pady=(4, 8), sticky='w')

# interval options
interval_frame = tk.Frame(main_frame, bg='white')
interval_frame.grid(row=3, column=0, padx=6, pady=6, sticky='ew')
intervalLabel = tk.Label(interval_frame, text="Interval", bg="white", font=("arial", 11, "bold"))  # smaller font
intervalLabel.grid(row=0, column=0, sticky="w", padx=6, pady=4)

for i, (label, value) in enumerate([('1D', DAY1), ('5D', DAY5), ('1M', MONTH1), ('1Y', YEAR1)], start=1):
    tk.Radiobutton(interval_frame, text=label, value=value, bg='white', fg='black',
                   font=('arial', 9, 'bold'),  # smaller radio buttons
                   command=change_interval, variable=interval_variable).grid(row=0, column=i, padx=6, pady=4,
                                                                             sticky='w')

# Quit button
quit_btn = tk.Button(main_frame, text='Quit', width=5, height=1, bg='#eee', cursor='hand2', command=quit_btn)
quit_btn.grid(row=6, column=1, padx=6, pady=6, sticky='e')

main_window.mainloop()