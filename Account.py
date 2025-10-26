import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime

# 檔案名稱，用於儲存和載入所有記錄
FILE_NAME = 'prepaid_records.txt'

def load_records():
    """從檔案中讀取所有記錄並解析為字典列表。"""
    records = []
    if not os.path.exists(FILE_NAME):
        # 如果檔案不存在，則建立它
        with open(FILE_NAME, 'w', encoding='utf-8') as f:
            pass
        return records
    
    with open(FILE_NAME, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                date, item, amount_str, reimbursed = line.split(',')
                records.append({
                    'date': date.strip(),
                    'item': item.strip(),
                    'amount': float(amount_str.strip()),
                    'reimbursed': reimbursed.strip()
                })
            except ValueError:
                print(f"⚠️ 忽略無效的記錄行: {line}")
    return records

def save_new_record_to_file(date, item, amount, reimbursed):
    """將一條新記錄附加到檔案末尾。"""
    try:
        amount_float = float(amount)
    except ValueError:
        return False, "金額必須是有效的數字。"
    
    # 簡單的格式檢查
    if not date or not item or amount_float <= 0 or reimbursed not in ['Yes', 'No']:
        return False, "輸入資料不完整或無效。"

    # 格式化為檔案行
    new_record = f"{date},{item},{amount_float:.2f},{reimbursed}\n"
    
    try:
        with open(FILE_NAME, 'a', encoding='utf-8') as f:
            f.write(new_record)
        return True, "記錄已成功新增。"
    except Exception as e:
        return False, f"寫入檔案失敗: {e}"


class PrepaidApp(tk.Tk):
    """預付現金記錄的 GUI 應用程式主類。"""
    def __init__(self):
        super().__init__()
        self.title("預付現金與報銷記錄系統")
        self.geometry("850x650")
        
        # 設置樣式
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=('Inter', 10))
        style.configure("TButton", font=('Inter', 10, 'bold'), padding=6, background="#4a86e8", foreground="white")
        style.map("TButton", background=[('active', '#3c69ba')])
        
        # 狀態變數
        self.records = load_records()
        self.reimbursement_status = tk.StringVar(value='No')

        self.create_widgets()
        self.update_display() # 首次載入時顯示記錄

    def create_widgets(self):
        """建立應用程式的所有 GUI 組件。"""
        
        # --- 頂部輸入框架 ---
        input_frame = ttk.Frame(self, padding="15 15 15 15", relief="groove")
        input_frame.pack(fill='x', padx=10, pady=10)

        # 標籤和輸入欄位配置
        fields = [
            ("日期 (YYYY-MM-DD):", 'date_entry'), 
            ("項目描述:", 'item_entry'), 
            ("預付金額:", 'amount_entry')
        ]
        
        row_num = 0
        self.entry_vars = {} # 用於儲存輸入變數

        for label_text, var_name in fields:
            label = ttk.Label(input_frame, text=label_text, width=15)
            label.grid(row=row_num, column=0, sticky='w', pady=5, padx=5)
            
            var = tk.StringVar()
            entry = ttk.Entry(input_frame, textvariable=var, width=30)
            entry.grid(row=row_num, column=1, sticky='ew', pady=5, padx=5)
            self.entry_vars[var_name] = var
            
            row_num += 1

        # 是否已收回款項 (單選按鈕)
        reimbursed_label = ttk.Label(input_frame, text="已收回款項:", width=15)
        reimbursed_label.grid(row=3, column=0, sticky='w', pady=5, padx=5)

        ttk.Radiobutton(input_frame, text="是 (Yes)", variable=self.reimbursement_status, value='Yes').grid(row=3, column=1, sticky='w', padx=5)
        ttk.Radiobutton(input_frame, text="否 (No)", variable=self.reimbursement_status, value='No').grid(row=3, column=1, padx=5, sticky='e')
        
        # 新增按鈕
        add_button = ttk.Button(input_frame, text="新增記錄", command=self.add_record, cursor="hand2")
        add_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        # --- 中部 Treeview 顯示框架 ---
        display_frame = ttk.Frame(self, padding="10")
        display_frame.pack(fill='both', expand=True, padx=10)

        # 建立 Treeview (表格)
        columns = ("date", "item", "amount", "reimbursed")
        self.tree = ttk.Treeview(display_frame, columns=columns, show='headings', height=15)
        
        # 定義欄位標題
        self.tree.heading("date", text="日期", anchor='w')
        self.tree.heading("item", text="項目", anchor='w')
        self.tree.heading("amount", text="預付金額", anchor='e')
        self.tree.heading("reimbursed", text="已收回款", anchor='center')
        
        # 定義欄位寬度
        self.tree.column("date", width=120, anchor='w')
        self.tree.column("item", width=300, anchor='w')
        self.tree.column("amount", width=120, anchor='e')
        self.tree.column("reimbursed", width=100, anchor='center')

        # 捲動條
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- 底部總計框架 ---
        total_frame = ttk.Frame(self, padding="10 15 10 15", relief="raised")
        total_frame.pack(fill='x', padx=10, pady=5)
        
        # 總計標籤
        self.total_label = ttk.Label(total_frame, 
                                     text="每用支出總數: $0.00", 
                                     font=('Inter', 14, 'bold'), 
                                     foreground="#d90000")
        self.total_label.pack(side='right', padx=20)
        
        ttk.Label(total_frame, 
                  text="總計:", 
                  font=('Inter', 14, 'bold')).pack(side='right')

    def add_record(self):
        """處理新增記錄的按鈕點擊事件。"""
        date = self.entry_vars['date_entry'].get().strip()
        item = self.entry_vars['item_entry'].get().strip()
        amount = self.entry_vars['amount_entry'].get().strip()
        reimbursed = self.reimbursement_status.get()

        # 嘗試將記錄儲存到檔案
        success, message = save_new_record_to_file(date, item, amount, reimbursed)

        if success:
            messagebox.showinfo("成功", "新增記錄成功！")
            # 清空輸入欄位
            for var in self.entry_vars.values():
                var.set("")
            self.reimbursement_status.set('No')
            # 重新載入並更新顯示
            self.records = load_records()
            self.update_display()
        else:
            messagebox.showerror("錯誤", message)

    def update_display(self):
        """清空 Treeview 並重新載入所有記錄。"""
        # 清空現有的 Treeview 內容
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        # 插入新記錄
        for record in self.records:
            # 格式化金額以確保兩位小數
            amount_str = f"{record['amount']:.2f}"
            self.tree.insert('', tk.END, values=(
                record['date'], 
                record['item'], 
                amount_str, 
                record['reimbursed']
            ))
            
        # 更新總計
        self.calculate_totals()

    def calculate_totals(self):
        """計算並顯示所有預付金額的總和。"""
        total_spent = sum(record['amount'] for record in self.records)
        self.total_label.config(text=f"每用支出總數: ${total_spent:,.2f}")


if __name__ == "__main__":
    app = PrepaidApp()
    app.mainloop()