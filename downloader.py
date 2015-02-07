import os
import re
import time
import requests
try:
    from lxml import etree
    sys_praser = "lxml"
except:
    from bs4 import BeautifulSoup
    sys_praser = "BeautifulSoup"

class BookDownloader(object):

    def __init__(self,username,password,scale = 1):
        self.web = requests.session()

        self.username = username
        self.password = password

        # scale 图片质量，可选 1，2，4，8
        # 1的质量最好
        self.scale = scale
        self.books = []
        self.choice = 0
        self.pageNum = 0

    def begin(self):

        self.login()
        print("login")
        self.get_loan_books_info()
        self.get_user_choice()
        self.get_choice_book_info()

        # 创建文件夹
        self.floder_path = os.path.abspath('.') + "/" + self.books[self.choice]['name'] + "/"
        if not os.path.exists(self.floder_path):
            os.mkdir(self.floder_path)

        # 开始下载
        print("Downloading " + "【 " + self.books[self.choice]['name'] + " 】 -------->>>>>>  " + self.floder_path)
        self.download()
        print("Download " + "【 " + self.books[self.choice]['name'] + " 】" + "finished")

    def login(self):

        url = 'https://openlibrary.org/account/login'
        post_data = {}
        post_data['username'] = username
        post_data['password'] = password
        post_data['redirect'] = 'https://openlibrary.org/'
        post_data['login']    = 'Log In'

        r = self.web.post(url,post_data)

        assert r.status_code == 200

    def get_loan_books_info(self):

        loan_url = 'https://openlibrary.org/account/loans'
        r = self.web.get(loan_url)
        assert r.status_code == 200


        # prase html by lxml
        if sys_praser == "lxml":

            tree = etree.HTML(r.text)
            all_tr = tree.xpath('//*[@id="borrowTable"][1]/table/tbody/tr')
            tree = etree.HTML(r.text)
            for tr in all_tr:
                book = {}
                book['name']   = tr.xpath('./td[2]/span[1]/a/strong')[0].text
                book['author'] = tr.xpath('./td[2]/span[2]/span/a')[0].text
                book['url'] = 'https://openlibrary.org' + tr.xpath('.//td[4]/form[1]')[0].attrib["action"]
                self.books.append(book)
        # prase html by beautiful soup
        else:
            soup = BeautifulSoup(r.text)
            all_tr = soup.find_all(id = "borrowTable")[0].table.tbody.find_all("tr")
            for tr in all_tr:
                book = {}
                book['name']   = tr.find_all("td")[1].find_all("span")[0].a.strong.text.strip()
                book['author'] = tr.find_all("td")[1].find_all("span")[1].text.strip()
                book['url'] = 'https://openlibrary.org' + tr.find_all("td")[3].find_all("form")[0]["action"]
                self.books.append(book)

    def get_user_choice(self):

        # 获得最长书名
        max_len = 0

        for book in self.books:
            length = len(book['name'])
            if length > max_len:
                max_len = length
        format = "%-" + str(max_len + 5) + "s %s"
        i = 1
        print('-------------------------------------')
        for book in self.books:
            name = str(i) + ". " + "【 " + book['name']
            author = " 】<<<<<<-------- " + book['author']
            print(format % (name,author))
            i = i + 1
        print('-------------------------------------')
        print("Which book do you want to download")
        n = len(self.books)
        if n <= 0:
            print("Have no book to download")
            exit(0)
        while 1:
            c = input("Input Number " + "【 " + "1" + " ~ " + str(n) +  " 】:")
            c = int(c)
            if 0 < c <= n:
                self.choice = c - 1
                break
            else:
                print("Input error,try again")


    def get_choice_book_pageNum(self,url,args = ""):

        params = {}
        for p in args.split("&"):
            v = p.split("=")
            params[v[0]] = v[1]

        r = self.web.get(url,params = params)
        assert r.status_code == 200
        pattern = "br.pageNums = \[((?:.|\n)*?)\]"
        vec = re.findall(pattern,r.text)[0]
        self.pageNum = len(vec.split(","))

    def get_choice_book_info(self):

        #  1.构造链接
        #  2.获得书本的页数

        post_url = self.books[self.choice]['url']
        post_data = {}
        post_data['action'] = 'read'
        post_data['ol_host'] = 'openlibrary.org'

        r = self.web.post(post_url,post_data)
        assert r.status_code == 200



        # 获取下面这个字符串
        #//ia801409.us.archive.org/BookReader/BookReaderJSIA.php?
        # id=objectorientedpr00coxb
        # itemPath=/3/items/objectorientedpr00coxb
        # server=ia801409.us.archive.org
        # subPrefix=objectorientedpr00coxb
        # version=3.1.3

        # 构造成下面的形式，得到图片 url 模板
        # //ia801409.us.archive.org/BookReader/BookReaderImages.php?
        # zip = itemPath + "/" + id + "_jp2.zip"
        # file = id + "_jp2" + "/" + subPrefix + "_" + number + ".jpg"
        # &scale=8&rotate=0
        if sys_praser == "lxml":
            tree = etree.HTML(r.text)
            src = "https:" + tree.xpath('//html/body/script[3]')[0].attrib["src"]
        else:
            soup = BeautifulSoup(r.text)
            src = "https:" + soup.html.body.find_all("script")[2]["src"]
        print (src)

        vec_0 = src.split("?")[1].split("&")

        id       = vec_0[0].split("=")[1]
        itemPath = vec_0[1].split("=")[1]
        server   = vec_0[2].split("=")[1]
        subPrefix= vec_0[3].split("=")[1]

        zip = itemPath + "/" + id + "_jp2.zip"
        file = id + "_jp2" + "/" + subPrefix + "_"

        self.url_1 = "https://" + server + "/BookReader/BookReaderImages.php?" + "zip=" + zip + "&" + "file=" + file
        self.url_2 = ".jp2&" + "scale=" + str(self.scale) + "&rotate=0"

        # 获取书本页数
        self.get_choice_book_pageNum(src.split("?")[0],src.split("?")[1])
    def number2str(self,i):

        # 将数字前面补0到4位，转化为字符串
        j = 1
        k = i
        while int(k/10) > 0:
            j = j+1
            k = int(k/10)
        number = "0" * (4 - j) + str(i)

        return number

    def get_page_url(self,i):

        number = self.number2str(i)
        return self.url_1 + number + self.url_2

    def save_page(self,i,content):

        file_name = self.floder_path + self.number2str(i) + '.jpg'
        f = open(file_name,'wb')
        f.write(content)
        f.close()


    def is_page_downloaded(self,i):

        return os.path.isfile(self.floder_path + self.number2str(i) + '.jpg')

    def download(self):

        for i in range(1,self.pageNum + 1):

            if self.is_page_downloaded(i):
                continue
            while 1:
                try:

                    url = self.get_page_url(i)
                    #print(url)
                    r = self.web.get(url,verify = False)
                except:
                    print("network error on page " + str(i)  + ",I'll try again")
                    time.sleep(1)
                    continue
                break

            # 下载成功，保存图片
            if r.status_code == 200:
                print("Page " + str(i) + " downloaded")
                self.save_page(i,r.content)

            # 下载失败，重新下载该页
            elif not i == self.pageNum:
                print("page " + str(i) + " faild! status_code = " + str(r.status_code) + ",I'll try again")
                i = i - 1
                time.sleep(1)
                continue

if __name__ == '__main__':


    # https://openlibrary.org/
    username = ''
    password = ''
    # scale 代表图片质量，可选 1，2
    # 1 的质量最好，约1M
    # 建议2，除非网速很好
    scale    = 2

    downloader = BookDownloader(username,password,scale)
    downloader.begin()











