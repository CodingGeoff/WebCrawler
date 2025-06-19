# -*- coding: utf-8 -*-

import tkinter
import customtkinter
import pyperclip
import requests
from markdownify import markdownify as md
from tkinter import filedialog, messagebox
import trafilatura
from DrissionPage import SessionPage, SessionOptions
import threading
import re
from urllib.parse import urlparse, urlunparse, urljoin
from datetime import datetime
from collections import deque
from pathlib import Path
from configparser import ConfigParser
from bs4 import BeautifulSoup
import time
import importlib.resources

# --- 主应用窗口设置 ---
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- 实例变量 ---
        self.history = deque(maxlen=20)
        self.history_var = customtkinter.StringVar(value="历史记录")

        # --- 窗口配置 ---
        self.title("网页转 Markdown Pro (终极版) 🚀 v6.0")
        self.geometry("1000x800")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- 顶部框架 ---
        self.top_frame = customtkinter.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.url_label = customtkinter.CTkLabel(self.top_frame, text="网页链接:", font=customtkinter.CTkFont(size=14))
        self.url_label.grid(row=0, column=0, padx=(20, 10), pady=10)
        self.url_entry = customtkinter.CTkEntry(self.top_frame, placeholder_text="请在此处输入或粘贴 URL")
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.paste_button = customtkinter.CTkButton(self.top_frame, text="📋 粘贴", width=80, command=self.paste_from_clipboard)
        self.paste_button.grid(row=0, column=2, padx=5, pady=10)
        self.paste_and_convert_button = customtkinter.CTkButton(self.top_frame, text="📋⚡ 粘贴并转换", width=120, command=self.paste_and_convert)
        self.paste_and_convert_button.grid(row=0, column=3, padx=5, pady=10)
        self.fetch_button = customtkinter.CTkButton(self.top_frame, text="⚡ 开始转换", width=100, command=self.start_single_conversion_thread)
        self.fetch_button.grid(row=0, column=4, padx=(5, 20), pady=10)

        # --- 选项框架 ---
        self.options_frame = customtkinter.CTkFrame(self)
        self.options_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.options_frame.grid_columnconfigure(5, weight=1)
        self.image_option_label = customtkinter.CTkLabel(self.options_frame, text="图片处理:")
        self.image_option_label.grid(row=0, column=0, padx=(20, 5), pady=10)
        self.image_option_menu = customtkinter.CTkOptionMenu(self.options_frame, values=["保留原始链接", "下载到本地", "删除所有图片"])
        self.image_option_menu.set("下载到本地")
        self.image_option_menu.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        self.toc_checkbox = customtkinter.CTkCheckBox(self.options_frame, text="生成目录(TOC)")
        self.toc_checkbox.select()
        self.toc_checkbox.grid(row=0, column=2, padx=10, pady=10)
        self.clean_link_checkbox = customtkinter.CTkCheckBox(self.options_frame, text="清理链接追踪参数")
        self.clean_link_checkbox.select()
        self.clean_link_checkbox.grid(row=0, column=3, padx=10, pady=10)
        self.history_menu = customtkinter.CTkOptionMenu(self.options_frame, variable=self.history_var, values=["历史记录"], command=self.load_from_history)
        self.history_menu.grid(row=0, column=4, padx=10, pady=10)
        self.theme_switch = customtkinter.CTkSwitch(self.options_frame, text="夜间模式", command=lambda: customtkinter.set_appearance_mode("Dark" if self.theme_switch.get() else "Light"))
        self.theme_switch.grid(row=0, column=6, padx=(20, 20), pady=10, sticky="e")

        # --- 中部文本框 ---
        self.textbox = customtkinter.CTkTextbox(self, corner_radius=10, font=customtkinter.CTkFont(family="Consolas", size=14))
        self.textbox.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.textbox.insert("0.0", "转换后的 Markdown 内容将显示在这里...")
        self.textbox.bind("<KeyRelease>", self.update_word_count)

        # --- 状态栏框架 ---
        self.status_bar = customtkinter.CTkFrame(self, height=30)
        self.status_bar.grid(row=3, column=0, padx=20, pady=(5, 0), sticky="ew")
        self.status_label = customtkinter.CTkLabel(self.status_bar, text="状态: 待命", font=customtkinter.CTkFont(size=12))
        self.status_label.pack(side="left", padx=10, pady=5)
        self.progress_bar = customtkinter.CTkProgressBar(self.status_bar)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left", padx=10, pady=5, expand=True, fill="x")
        self.word_count_label = customtkinter.CTkLabel(self.status_bar, text="字数: 0 | 字符: 0", font=customtkinter.CTkFont(size=12))
        self.word_count_label.pack(side="right", padx=10, pady=5)

        # --- 底部框架 ---
        self.bottom_frame = customtkinter.CTkFrame(self)
        self.bottom_frame.grid(row=4, column=0, padx=20, pady=(5, 20), sticky="ew")
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.copy_button = customtkinter.CTkButton(self.bottom_frame, text="📋 复制全部内容", command=self.copy_to_clipboard)
        self.copy_button.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.batch_button = customtkinter.CTkButton(self.bottom_frame, text="📂 批量处理", fg_color="green", hover_color="dark green", command=self.start_batch_processing_thread)
        self.batch_button.grid(row=0, column=2, padx=20, pady=10)
        self.save_button = customtkinter.CTkButton(self.bottom_frame, text="💾 保存为 Markdown (.md)", command=self.save_as_markdown)
        self.save_button.grid(row=0, column=3, padx=20, pady=10, sticky="e")

    def _get_trafilatura_config(self):
        """
        创建一个稳健的 Trafilatura 配置对象，确保在打包后也能正常工作。
        """
        # 步骤 1: 创建一个 ConfigParser 实例，并禁用插值法，防止 '%' 符号引发错误。
        config = ConfigParser(interpolation=None)

        # 步骤 2: 定义一个包含所有必需默认值的“主”字典。
        # 这些值直接取自 trafilatura 的官方 config.ini，是保证程序运行的“安全网”。
        # 这样可以 100% 避免 "No option '...' in section: 'DEFAULT'" 错误。
        master_defaults = {
            'min_extracted_size': '2500', 'min_output_size': '250',
            'min_text_length': '70', 'max_text_length': '200000',
            'max_file_size': '2000000', 'min_extracted_comm_size': '500',
            'min_output_comm_size': '150', 'max_duplicate_counter': '2',
            'max_repeated_len': '100', 'min_overall_score': '0.5',
            'min_element_score': '0.1', 'author_blacklist': 'author, byline, user, by, e-?mail',
            'url_blacklist': r'https?://(www\.)?google.com/search, https?://(www\.)?bing.com/search, https?://search.yahoo.com/search',
            'min_duplcheck_size': '1000', 'max_link_density': '0.25',
            'max_heading_density': '0.5', 'max_blockquote_density': '0.5',
            'table_min_rows': '2', 'table_min_cols': '2',
            'min_links_in_table': '0', 'extensive_date_search': 'True',
            'date_search_xpath': '//time | //*[contains(@class, "date")] | //*[contains(@class, "time")] | //*[contains(@id, "date")] | //*[contains(@id, "time")]',
            # [关键修正] 对含有'%'的值进行转义，或使用 %%
            'date_extraction_params': '{"original_date":false, "extensive_search":true, "outputformat":"%%Y-%%m-%%d"}',
            'image_extraction_params': '{"fast":true, "output_format":"absolute"}',
            "max_repetitions": "5", "min_file_size": "0"
        }
        
        # 步骤 3: 将我们的“安全网”配置加载到 ConfigParser 中。
        # 此时，config 对象已经包含了所有必要的默认值。
        config['DEFAULT'] = master_defaults

        # 步骤 4: (可选但推荐) 尝试读取库中真正的 config.ini 文件。
        # 如果程序没有被打包，这能读取到最新的、用户可能修改过的配置。
        # 如果程序被打包成exe，这一步会失败，但没关系，因为我们已经有“安全网”配置了。
        try:
            # 使用 importlib.resources 是在包内查找数据文件的标准、可靠方法。
            config_string = importlib.resources.read_text('trafilatura', 'config.ini')
            config.read_string(config_string)
        except Exception as e:
            # 在打包后的环境中，找不到文件是预期行为，无需报错。
            # 我们可以在这里加一句日志用于调试，但对于最终用户来说应该静默处理。
            print(f"Info: Could not load external trafilatura config.ini (this is normal for a packaged .exe), falling back to complete internal defaults. Details: {e}")

        return config


    # --- 线程启动器 ---
    def start_single_conversion_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            self.show_error("输入错误", "请输入一个有效的 URL！")
            return
        self._toggle_buttons(False)
        thread = threading.Thread(target=self.single_conversion_worker, args=(url,))
        thread.daemon = True
        thread.start()

    def start_batch_processing_thread(self):
        txt_path = filedialog.askopenfilename(title="请选择包含URL列表的txt文件", filetypes=[("Text files", "*.txt")])
        if not txt_path: return
        output_dir = filedialog.askdirectory(title="请选择保存Markdown文件的文件夹")
        if not output_dir: return
        self._toggle_buttons(False)
        thread = threading.Thread(target=self.batch_worker, args=(txt_path, output_dir))
        thread.daemon = True
        thread.start()

    # --- 核心工作逻辑 (线程中运行) ---
    def single_conversion_worker(self, url):
        self.after(0, lambda: self.textbox.delete("1.0", "end"))
        self.after(0, lambda: self.textbox.insert("1.0", f"开始处理链接: {url}\n\n"))
        md_content, page_title, error = self._process_url(url)
        if error:
            self.update_status(f"处理失败", color="red"); self.show_error("转换失败", error)
        else:
            self.after(0, lambda: self.textbox.delete("1.0", "end"))
            self.after(0, lambda: self.textbox.insert("1.0", md_content))
            self.after(0, self.update_word_count)
            self.update_status("转换完成！", color="green")
        self.after(100, lambda: self._toggle_buttons(True))
        self.after(500, lambda: self.update_progress(0))

    def batch_worker(self, txt_path, output_dir):
        try:
            with open(txt_path, 'r', encoding='utf-8') as f: urls = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.show_error("文件读取失败", f"无法读取txt文件: {e}"); self._toggle_buttons(True); return
        total = len(urls); success_count, fail_count = 0, 0; failed_urls = []
        for i, url in enumerate(urls):
            self.update_status(f"批量处理中 ({i+1}/{total})...", "yellow"); self.update_progress((i + 1) / total)
            md_content, page_title, error = self._process_url(url, output_dir_for_images=output_dir)
            if error:
                fail_count += 1; failed_urls.append(f"{url} (原因: {error})")
            else:
                success_count += 1
                try:
                    filename = self._sanitize_filename(page_title) + ".md"
                    save_path = Path(output_dir) / filename
                    with open(save_path, "w", encoding="utf-8") as f: f.write(md_content)
                except Exception as e:
                    fail_count += 1; failed_urls.append(f"{url} (原因: 文件保存失败 - {e})")
            time.sleep(0.1)
        summary = f"批量处理完成！\n\n成功: {success_count} 个\n失败: {fail_count} 个"
        if failed_urls: summary += "\n\n失败列表:\n" + "\n".join(failed_urls)
        self.update_status("批量处理完成！", "green"); self.show_message("任务完成", summary)
        self.after(100, lambda: self._toggle_buttons(True)); self.after(500, lambda: self.update_progress(0))

    def _process_url(self, url, output_dir_for_images=None):
        trafilatura_config = self._get_trafilatura_config()

        html_content, fetch_error = self._fetch_html(url, trafilatura_config)
        if fetch_error: return None, None, fetch_error
        try:
            page_title = self._extract_title(html_content) or url.split('/')[-1] or "untitled"
            if url not in self.history:
                self.history.appendleft(url); self.after(0, lambda: self.history_menu.configure(values=list(self.history)))
            
            # 使用 trafilatura 提取核心内容
            main_content_html = trafilatura.extract(
                html_content,
                include_comments=False,
                include_tables=True,
                favor_precision=True,
                config=trafilatura_config
            )

            # 如果 trafilatura 提取失败，则退回使用原始 HTML
            if not main_content_html:
                self.update_status("Trafilatura 提取失败，尝试完整转换", color="orange")
                main_content_html = html_content
                
            image_option = self.image_option_menu.get()
            if image_option != "保留原始链接":
                main_content_html = self._process_images(main_content_html, image_option, url, page_title, output_dir_for_images)
            
            if self.clean_link_checkbox.get():
                main_content_html = self._clean_hyperlinks(main_content_html)
            
            markdown_content = md(main_content_html, heading_style="ATX", bullets="*")
            
            final_md = []
            yaml_header = f"---\ntitle: {page_title}\nsource: {url}\ndate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n---\n\n"
            final_md.append(yaml_header)
            
            if self.toc_checkbox.get():
                toc = self._generate_toc(markdown_content)
                if toc: final_md.append("## 目录\n\n" + toc + "\n\n---\n\n")
            
            final_md.append(markdown_content)
            
            return "".join(final_md), page_title, None
        except Exception as e:
            # 捕获任何在内容处理阶段的错误
            return None, None, f"内容处理失败: {e}"

    def _fetch_html(self, url, config):
        # 尝试方法1: Trafilatura 自带的下载器
        try:
            self.update_status("抓取中 (方法1: Trafilatura)...", "yellow")
            html = trafilatura.fetch_url(url, config=config)
            if html: return html, None
        except Exception:
            pass # 失败则继续

        # 尝试方法2: 使用 requests
        try:
            self.update_status("抓取中 (方法2: Requests)...", "yellow")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text, None
        except Exception:
            pass # 失败则继续
            
        # 尝试方法3: 使用 DrissionPage (模拟浏览器)
        try:
            self.update_status("抓取中 (方法3: DrissionPage)...", "yellow")
            options = SessionOptions()
            # 注意：打包时需要将 drivers 目录包含进去
            options.set_paths(driver_path=r'.\drivers')
            page = SessionPage(options)
            page.get(url, timeout=60)
            html = page.html
            page.quit()
            return html, None
        except Exception as e:
            return None, f"所有抓取方法均失败: {e}"

    # --- 辅助函数 (无变化) ---
    def _toggle_buttons(self, enabled):
        state = "normal" if enabled else "disabled"
        self.fetch_button.configure(state=state)
        self.paste_and_convert_button.configure(state=state)
        self.batch_button.configure(state=state)

    def _process_images(self, html, option, base_url, page_title, output_dir_base=None):
        soup = BeautifulSoup(html, 'html.parser')
        images = soup.find_all('img')
        if option == "删除所有图片":
            for img in images: img.decompose()
            return str(soup)
        
        if option == "下载到本地":
            if output_dir_base:
                image_dir = Path(output_dir_base) / (self._sanitize_filename(page_title) + "_images")
            else:
                # 对于单个文件转换，在当前目录创建
                image_dir = Path(self._sanitize_filename(page_title) + "_images")
            
            image_dir.mkdir(exist_ok=True, parents=True)
            
            for i, img in enumerate(images):
                src = img.get('src')
                if not src: continue
                
                try:
                    abs_src = urljoin(base_url, src)
                    response = requests.get(abs_src, stream=True, timeout=10)
                    response.raise_for_status()
                    
                    # 尝试从URL中获取一个合理的文件扩展名
                    file_ext = Path(urlparse(abs_src).path).suffix or '.jpg'
                    if len(file_ext) > 5 or not file_ext.startswith('.'): file_ext = '.jpg'

                    file_name = f"image_{i+1}{file_ext}"
                    file_path = image_dir / file_name

                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(8192): f.write(chunk)

                    # 更新图片路径为相对路径
                    # 在批量处理时，md文件和图片文件夹在同一目录，所以路径是 '图片文件夹名/图片名'
                    if output_dir_base:
                        img['src'] = (Path(image_dir.name) / file_name).as_posix()
                    else: # 单个文件处理时，直接用绝对或相对路径
                        img['src'] = file_path.as_posix()
                        
                except Exception:
                    # 如果下载失败，保留原始链接
                    continue
            return str(soup)
        return html

    def _clean_hyperlinks(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a', href=True):
            try:
                parsed_url = urlparse(a['href'])
                # 只保留 scheme, netloc, path，去除查询参数和片段
                a['href'] = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
            except Exception:
                continue # 如果URL无效，则跳过
        return str(soup)

    def _generate_toc(self, markdown_content):
        toc, unique_check = [], set()
        # 只匹配 ## 和 ### 级别的标题
        headers = re.findall(r'^(##|###)\s+(.*)', markdown_content, re.MULTILINE)
        for header in headers:
            level, title = len(header[0]), header[1].strip()
            # 创建一个 GitHub/GitLab 兼容的锚点链接
            link_id = re.sub(r'[^\w\s-]', '', title).strip().lower()
            link_id = re.sub(r'[-\s]+', '-', link_id)
            
            # 处理重复的标题
            if link_id in unique_check:
                temp_id, count = link_id, 1
                while temp_id in unique_check:
                    temp_id = f"{link_id}-{count}"
                    count += 1
                link_id = temp_id
            
            unique_check.add(link_id)
            
            indent = "  " * (level - 2) # h2不缩进, h3缩进
            toc.append(f"{indent}- [{title}](#{link_id})")
        return "\n".join(toc)

    def _sanitize_filename(self, filename):
        return re.sub(r'[\\/*?:"<>|]', "", filename).strip() or "unnamed_file"

    def _extract_title(self, html_content):
        if not html_content: return ""
        match = re.search(r'<title.*?>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""

    def update_word_count(self, event=None):
        content = self.textbox.get("1.0", "end-1c")
        char_count = len(content)
        word_count = len(re.findall(r'\S+', content))
        self.word_count_label.configure(text=f"字数: {word_count} | 字符: {char_count}")

    def paste_from_clipboard(self):
        try:
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, pyperclip.paste())
        except Exception as e:
            self.show_error("剪贴板错误", f"无法读取剪贴板内容: {e}")

    def paste_and_convert(self):
        self.paste_from_clipboard()
        self.start_single_conversion_thread()

    def copy_to_clipboard(self):
        try:
            pyperclip.copy(self.textbox.get("1.0", "end-1c"))
            self.show_message("成功", "Markdown 内容已复制到剪贴板！")
        except Exception as e:
            self.show_error("复制失败", f"无法复制到剪贴板: {e}")

    def save_as_markdown(self):
        content = self.textbox.get("1.0", "end-1c")
        if not content or content.startswith("转换后的 Markdown 内容将显示在这里..."):
            self.show_warning("内容为空", "没有可保存的内容。")
            return
        
        page_title_match = re.search(r'title:\s*(.*)', content)
        default_filename = self._sanitize_filename(page_title_match.group(1).strip() if page_title_match else "untitled") + ".md"
        
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".md",
            filetypes=[("Markdown 文件", "*.md"), ("所有文件", "*.*")],
            title="选择保存位置"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f: f.write(content)
                self.show_message("保存成功", f"文件已成功保存到:\n{file_path}")
            except Exception as e:
                self.show_error("保存失败", f"无法保存文件: {e}")

    def load_from_history(self, choice):
        if choice and choice != "历史记录":
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, choice)
            self.start_single_conversion_thread()
        self.history_var.set("历史记录")

    def update_status(self, message, color="gray"):
        self.after(0, lambda: self.status_label.configure(text=f"状态: {message}", text_color=color))

    def update_progress(self, value):
        self.after(0, lambda: self.progress_bar.set(value))

    def show_error(self, title, message):
        self.after(0, lambda: messagebox.showerror(title, message))

    def show_warning(self, title, message):
        self.after(0, lambda: messagebox.showwarning(title, message))

    def show_message(self, title, message):
        self.after(0, lambda: messagebox.showinfo(title, message))

if __name__ == "__main__":
    app = App()
    app.mainloop()