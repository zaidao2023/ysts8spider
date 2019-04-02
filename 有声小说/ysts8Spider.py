"""
@author:qh
@datetime:2019-3-5
@mood:<(*￣▽￣*)/
"""

# import time
# from multiprocessing import Pool
# from PIL import ImageTk, Image
import requests
import os
import threading
from queue import Queue
from lxml import etree
from threading import Thread

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tkinter import *
from tkinter import ttk
from tkinter import PhotoImage
from bs4 import BeautifulSoup as bs
from urllib.parse import quote
from urllib.parse import unquote


class Ysts8(object):
    def __init__(self):
        self.app = None
        self.book_list = []
        self.book_info = {}
        self.book_title = None
        self.file_path = None

    # 搜索关键词
    def search_keywords(self):
        lbx = self.app.children['lbx']
        lbx.delete(0, END)
        en = self.app.children['en']
        if en:
            keyword = quote(en.get(), encoding='gb2312').upper()
            """%B6%B7%C2%DE%B4%F3%C2%BD"""
            def parse_page(page_num=1):
                url = 'https://www.ysts8.com/Ys_so.asp?stype=1&keyword={}&page={}'.format(keyword, page_num)
                res = requests.get(url, headers={'User-Agent': UserAgent(verify_ssl=False).random, 'Host': 'www.ysts8.com'}).content.decode('gb2312', errors='ignore')
                soup = bs(res, 'lxml')
                a_href_obj = soup.select('body > div.toolbox > div.pingshu_ysts8 > ul > li > a')
                for a_href in a_href_obj:
                    info = a_href.get_text() + '    '
                    href = 'https://www.ysts8.com/{}'.format(a_href.get('href'))
                    self.book_info.update({
                        info: href
                    })
                    lbx = self.app.children['lbx']
                    lbx.insert(END, info)
                try:
                    _page_num = re.findall('<a href=(.*?)>下一页</a>', res)[0].split('&page=')[-1]
                except IndexError:
                    print('查询完毕！')
                    return
                else:
                    parse_page(_page_num)
            parse_page()

    # 开始下载
    def download(self, event):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(executable_path='driver/chromedriver', chrome_options=chrome_options)
        lbx = self.app.children['lbx']
        self.book_title = lbx.get(lbx.curselection())

        def _get_total_urls():
            href = self.book_info[self.book_title]
            res = requests.get(href, headers={
                'User-Agent': UserAgent(verify_ssl=False).random,
                'Host': 'www.ysts8.com'
            }).text
            html = etree.HTML(res)
            total_urls = html.xpath('//div[@class="ny_l"]//ul//li//a//@href')
            print(total_urls)
            return total_urls

        def _parse_download_page(url_list):
            re_urls = ['https://www.ysts8.com{}'.format(url) for url in url_list]
            return re_urls

        # 获取所有音频链接
        def _get_all_download_inks(base_url):
            """
            :param base_url:
            :return:
            """
            print('请求开始...')
            driver.get(base_url)
            print('请求中...')
            # time.sleep(0.5)
            frame = driver.find_element_by_xpath('//*[@id="play"]')
            driver.switch_to.frame(frame)
            select = (By.ID, 'jp_audio_0')
            audio_num = base_url.split('_')[-1].split('.')[0]
            try:
                WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(select))
                select = driver.find_element_by_id('jp_audio_0')
                audio = select.get_attribute('src')
                if audio:
                    _save(audio)
                else:
                    print('重新下载第{}集...'.format(audio_num))
                    _get_all_download_inks(base_url)
            except TimeoutError:
                driver.quit()

        def _save(url):
            print(unquote(url))
            res = requests.get(url, headers={
                'User-Agent': UserAgent(verify_ssl=False).random
            })
            file_name = url.split('?')[0].split('/')[-1]
            file_name = unquote(file_name)

            print(file_name)
            save_path = re.sub(r'[\/\\\:\*\?\"\<\>\|]', '_', t.name).strip()
            if not os.path.exists(save_path):
                os.mkdir(save_path)
            pathname = '{}/{}'.format(save_path, file_name)
            with open(pathname, 'wb+') as f2:
                f2.write(res.content)
            print('{}下载完成！'.format(file_name))

        def create_canvas(fill_rec, canvas, i, length, x):
            def change_schedule(fil_rec, cvs, now_schedule, all_schedule, var_x):
                cvs.coords(fil_rec, (0, 0, (now_schedule / all_schedule) * 380, 25))
                self.app.update()
                var_x.set(str(round(now_schedule / all_schedule * 100, 2)) + '%')
                if round(now_schedule / all_schedule * 100, 2) == 100.00:
                    var_x.set("完成")
                    self.app.update()
            change_schedule(fill_rec, canvas, i + 1, length, x)

        def _main():
            total_urls = _get_total_urls()
            re_urls = _parse_download_page(total_urls)
            canvas = self.app.children['canvas']
            fill_rec = canvas.create_rectangle(0, 0, 0, 25, outline="", width=0, fill="#4c4f8b")
            x = StringVar()
            Label(self.app, textvariable=x, bg='#f1f1f1').place_configure(x=500, y=293)
            length = len(re_urls)
            for index, re_url in enumerate(re_urls):
                _get_all_download_inks(re_url)
                create_canvas(fill_rec, canvas, index, length, x)
                self.app.update()

        # q = Queue()
        t = Thread(target=_main, name='{}'.format(self.book_title))
        t.start()
        print(t, t.name)

    def create_app(self):
        window = Tk()
        ww = window.winfo_screenwidth()
        wh = window.winfo_screenheight()
        sw = 600
        sh = 340
        x = int((ww - sw) / 2)
        y = int((wh - sh) / 2)
        window.geometry('{}x{}+{}+{}'.format(sw, sh, x, y))
        window.resizable(0, 0)
        window.title('有声听书播放下载器！')

        # 加左上角图标
        window.iconbitmap('img/icon.ico')

        # 加图片
        img = PhotoImage(file='img/book.png')
        lb = Label(window, image=img, )
        lb.image = img
        lb.place(x=40, y=20)

        # ttk控件加样式
        style = ttk.Style()
        style.configure('BW.TEntry', foreground='#4c4f8b', background='white')

        en = ttk.Entry(window, name='en', style='BW.TEntry')
        en.place_configure(width=320, height=30, x=110, y=30)
        en.focus_set()
        ttk.Button(window, text='查询', command=self.search_keywords).place_configure(height=30, x=441, y=30)
        lbx = Listbox(window, name='lbx', font=('simhei', 14, 'bold'), fg='#4c4f8b')
        sb = Scrollbar(lbx)
        sb.pack(side=RIGHT, fill=Y)
        sb2 = Scrollbar(lbx, orient=HORIZONTAL)
        sb2.pack(side=BOTTOM, fill=X)
        lbx.config(xscrollcommand=sb2.set)
        lbx.config(yscrollcommand=sb.set)
        sb.config(command=lbx.yview)
        sb2.config(command=lbx.xview)
        lbx.bind('<Double-Button-1>', self.download)
        lbx.place_configure(width=500, height=200, x=40, y=80)
        window.bind('<Return>', lambda event: self.search_keywords())
        # ttk.Label(window, text='存储路径：').place_configure(x=270, y=294)
        # ttk.Entry(window, ).place_configure(width=100, height=25, x=340, y=293)
        # ttk.Button(window, text='打开文件', command=self._call_back).place_configure(x=450, y=292)
        Label(window, text='下载进度：').place_configure(x=40, y=292)
        canvas = Canvas(window, name='canvas', bg='white')
        canvas.create_rectangle(0, 0, 380, 25, outline="", width=1, fill='#d0ccc0')
        canvas.place_configure(width=380, height=25, x=110, y=292)
        # window.bind('<Destroy>', self.close_thread)
        return window

    def main(self):
        self.app = self.create_app()
        self.app.mainloop()


new_app = Ysts8()
new_app.main()





