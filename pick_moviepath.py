import requests
from bs4 import BeautifulSoup
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from collections import OrderedDict


class MagnetLinkExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("电影天堂磁力链接提取器 v2.0")
        self.root.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # URL输入部分
        url_frame = ttk.LabelFrame(main_frame, text="输入电影URL", padding="10")
        url_frame.pack(fill=tk.X, pady=5)

        self.url_entry = ttk.Entry(url_frame, width=60)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        extract_btn = ttk.Button(url_frame, text="提取", command=self.extract_links)
        extract_btn.pack(side=tk.LEFT)

        # 结果展示部分
        result_frame = ttk.LabelFrame(main_frame, text="提取结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            height=20
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 底部按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        save_btn = ttk.Button(button_frame, text="保存到文件", command=self.save_to_file)
        save_btn.pack(side=tk.LEFT, padx=(0, 5))

        clear_btn = ttk.Button(button_frame, text="清空结果", command=self.clear_results)
        clear_btn.pack(side=tk.LEFT)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X)

    def extract_links(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("输入错误", "请输入有效的URL地址")
            return

        self.status_var.set("正在提取磁力链接...")
        self.root.update()

        try:
            # 使用OrderedDict自动去重并保持顺序
            magnet_links = list(OrderedDict.fromkeys(self.do_extract(url)))

            self.result_text.delete('1.0', tk.END)
            if magnet_links:
                self.result_text.insert(tk.END, "================================ 磁力链接下载地址================================\n\n")

                for idx, link in enumerate(magnet_links, 1):
                    # 完全清理HTML标签和多余字符
                    clean_link = re.sub(r'<[^>]+>', '', link).strip()
                    if clean_link:
                        self.result_text.insert(tk.END, f"{idx}. {clean_link}\n\n")

                count = len(magnet_links)
                self.result_text.insert(tk.END, f"\n共找到 {count} 个唯一磁力链接")
                self.status_var.set(f"提取完成，共找到 {count} 个唯一链接")
            else:
                self.result_text.insert(tk.END, "未找到有效 magnet 链接")
                self.status_var.set("未找到磁力链接")

        except Exception as e:
            messagebox.showerror("提取错误", f"提取过程中出错:\n{str(e)}")
            self.status_var.set("提取出错")

    def do_extract(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding or 'utf-8'
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        magnet_links = []

        # 改进的正则表达式，更严格匹配磁力链接
        magnet_pattern = re.compile(
            r'magnet:\?xt=urn:btih:[0-9A-Fa-f]{32,40}(?:&dn=[^&"\'\s]+)?',
            re.IGNORECASE
        )

        # 提取<a>标签中的磁力链接
        for a in soup.find_all("a", href=True):
            href = a["href"]
            match = magnet_pattern.search(href)
            if match:
                # 分割链接，只保留基础部分(去除tr参数和html标签)
                base_link = match.group().split('&tr=')[0].split('<')[0]
                magnet_links.append(base_link)

        # 提取纯文本中的磁力链接
        text_matches = magnet_pattern.finditer(response.text)
        for match in text_matches:
            base_link = match.group().split('&tr=')[0].split('<')[0]
            magnet_links.append(base_link)

        return magnet_links

    def save_to_file(self):
        content = self.result_text.get('1.0', tk.END).strip()
        if not content:
            messagebox.showwarning("保存错误", "没有内容可保存")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile="磁力链接下载地址.txt"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_var.set(f"文件已保存: {file_path}")
                messagebox.showinfo("保存成功", f"磁力链接已保存到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("保存失败", f"保存文件时出错:\n{str(e)}")
                self.status_var.set("保存失败")

    def clear_results(self):
        self.result_text.delete('1.0', tk.END)
        self.status_var.set("就绪")

'''
if __name__ == "__main__":
    root = tk.Tk()
    app = MagnetLinkExtractorApp(root)
    root.mainloop()
'''
def main():
    root = tk.Tk()
    app = MagnetLinkExtractorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()  # 添加此入口，以便 `setup.py` 可以调用
