from ttkthemes import ThemedTk
import datasource
import tkinter as tk
from tkinter import ttk
import view
import simulate_input


class Window(ThemedTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Cooling Fan Indicators')
        # self.resizable(False, False)

        # ============== Style ===============
        style = ttk.Style(self)
        style.configure('TopFrame.TLabel', font=('標楷體', 20))

        # =========== Top Frame =============
        topFrame = ttk.Frame(self)
        ttk.Label(topFrame, text='冷卻風扇生產指標', style='TopFrame.TLabel').pack()
        topFrame.pack(padx=20, pady=20)

        # =========== Bottom Frame ==========
        bottomFrame = ttk.Frame(self, padding=[10, 10, 10, 10])

        # =========== Selected Frame ==========
        self.selectedFrame = ttk.Frame(self, padding=[10, 10, 10, 10])

        # Refresh button
        icon_button = view.ImageButton(self.selectedFrame, command=lambda: datasource.load_from_sqlite())
        icon_button.pack()

        # Combobox to select sales
        sales_list = datasource.get_sales()
        print("Returned Sales List:", sales_list)  # Debugging
        self.sales_selected = tk.StringVar()  
        customer_cb = ttk.Combobox(
            self.selectedFrame, textvariable=self.sales_selected, values=sales_list, state='readonly'
        )
        self.sales_selected.set('請選擇業務名稱')

        # Correctly bind the event handler
        customer_cb.bind('<<ComboboxSelected>>', self.on_sales_selected)
        customer_cb.pack(anchor='n', pady=10)

        self.customerFrame = None
        self.selectedFrame.pack(side='left', fill='y')

        # =========== Right Frame ==========
        rightFrame = ttk.LabelFrame(bottomFrame, text="產品生產指標", padding=[10, 10, 10, 10])
        
        # TreeView columns
        columns = (
            'sales_id', 'sales_name', 'customer_id', 'order_id', 'yield_rate',
            'thru_put', 'order_date', 'deliver_date', 'factory'
        )
        self.tree = ttk.Treeview(rightFrame, columns=columns, show='headings')
        # self.tree.bind('<<TreeviewSelect>>', self.item_selected) #--working line--------
        # define headings
        self.tree.heading('sales_id', text='業務代號')
        self.tree.heading('sales_name', text='業務名稱')
        self.tree.heading('customer_id', text='客戶代號')
        self.tree.heading('order_id', text='訂單號碼')
        self.tree.heading('yield_rate', text='良率')
        self.tree.heading('thru_put',text='直通率')
        self.tree.heading('order_date', text='下單日期')
        self.tree.heading('deliver_date', text='交貨日期')
        self.tree.heading('factory', text='生產工廠')
        self.tree.column('sales_id', width=80,anchor="center")
        self.tree.column('sales_name', width=100,anchor="center")
        self.tree.column('customer_id', width=120,anchor="center")
        self.tree.column('order_id', width=80,anchor="center")
        self.tree.column('yield_rate', width=50,anchor="center")
        self.tree.column('thru_put', width=50,anchor="center")
        self.tree.column('order_date', width=100,anchor="center")
        self.tree.column('deliver_date', width=100,anchor="center")
        self.tree.column('factory', width=80, anchor="center")
        
        self.tree.pack(side='right')
        rightFrame.pack(side='right')
        bottomFrame.pack()

    def on_sales_selected(self, event):
        selected_sales = self.sales_selected.get()
        print(f"Selected sales: {selected_sales}")  # Debugging
        customers = datasource.get_customer_id(selected_sales)

        if self.customerFrame:
            self.customerFrame.destroy()

        self.customerFrame = view.CustomerFrame(master=self.selectedFrame, customers=customers)
        self.customerFrame.bind("<<Radio_Button_Selected>>", lambda e: self.radio_button_click())
        self.customerFrame.pack()

    def radio_button_click(self, event=None):
        selected_customer = self.customerFrame.selected_radio.get()
        if not selected_customer:
            print("Error: No customer selected. Exiting method.")
            return
        # Clear TreeView
        for children in self.tree.get_children():
            self.tree.delete(children)

        # Fetch and display data for the selected customer
        selected_data = datasource.get_selected_data(selected_customer)

        for record in selected_data:
            print(f"Inserting record into TreeView: {record}")  # Debugging
            self.tree.insert("", "end", values=record)


    def item_selected(self, event):
        for selected_item in self.tree.selection():
            record = self.tree.item(selected_item)
            dialog = view.MyCustomDialog(parent=self, title=f'Order Details - {record["values"][2]}', record=record['values'])
            values = record.get('values', [])
            print(f"Selected values: {values}")


def main():
    window = Window(theme="arc")
    window.mainloop()


if __name__ == '__main__':
    # Generate the simulated data
    csv_file = 'sales_orders.csv'
    db_file = 'sales_orders.db'
    table_name = 'sales_orders'

    # Call the function from the package
    data_frame = simulate_input.generate_sales_data(csv_filename=csv_file, db_filename=db_file, table_name=table_name)

    # Display the first few rows of the data
    print(data_frame.head())
    
    main()



#------------version changes-----------------------------------------------------
# main2.py  2024/11/28 13:35    show the treeview list on window 
#                               bug: same customer has different sales
                                