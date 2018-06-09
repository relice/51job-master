# coding=utf-8

from pprint import pprint
import csv
from collections import Counter

from bs4 import BeautifulSoup
from lxml import etree
import requests
import matplotlib.pyplot as plt

import jieba
from wordcloud import WordCloud
import pic_package
import os


class JobSpider():
    def __init__(self):
        self.company = []
        self.text = ""
        self.keyworld = ""
        self.headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/56.0.2924.87 Safari/537.36'
        }

    def job_spider(self):
        """ 爬虫入口 """
        self.keyworld = input("请输入你要查找的岗位名称:")
        url = "http://search.51job.com/list/010000%252C020000%252C030200%252C040000,000000" \
              ",0000,00,9,99," + self.keyworld + ",2,{}.html? lang=c&stype=1&postchannel=0000&workyear=99&" \
                                                 "cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0" \
                                                 "&confirmdate=9&fromType=1&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="

        print("数据源是:" + url)

        urls = [url.format(p) for p in range(1, 36)]
        for url in urls:
            r = requests.get(url, headers=self.headers).content.decode('gbk')
            bs = BeautifulSoup(r, 'lxml').find("div", class_="dw_table").find_all("div", class_="el")
            for b in bs:
                try:
                    href, post = b.find('a')['href'], b.find('a')['title']
                    locate = b.find('span', class_='t3').text
                    salary = b.find('span', class_='t4').text
                    d = {'href': href, 'post': post, 'locate': locate, 'salary': salary}
                    self.company.append(d)
                except Exception:
                    pass

    def post_require(self):
        """ 通过一级页面爬虫获得二级页面URL,爬取二级详情页的 职位描述,年龄,学历, 并做数据清洗 """

        # 切片获取前100条数据,避免数据太多线程堵塞
        for c in self.company[0:100]:
            r = requests.get(c.get('href'), headers=self.headers).content.decode('gbk')

            # 避免数据为空,异常自己出来
            try:
                bs = BeautifulSoup(r, 'lxml')
                # 获取二级页面 岗位描叙
                job_msg = bs.find('div', class_="bmsg job_msg inbox").get_text()
                s = job_msg.replace("举报", "").replace("分享", "").replace("\t", "").strip()

                # div[@class ="jtag inbox"] / div[@ class ="t1"] / span[@ class ="sp4"][1]
                # 获取二级页面 岗位年限,学历


                # 年限
                job_year = bs.find('div', class_="jtag inbox") \
                    .find('div', class_="t1") \
                    .select('span[class="sp4"]')[0].get_text()
                # 学历
                job_deu = bs.find('div', class_="jtag inbox") \
                    .find('div', class_="t1") \
                    .select('span[class="sp4"]')[1].get_text()

                print("工作经验:%s ,学历:%s" % (job_year, job_deu))

                # job_deu = BeautifulSoup(r, 'lxml').find('div', class_="bmsg job_msg inbox").get_text()

            except AttributeError as result:  # x这个变量被绑定到了错误的实例
                print('AttributeError: get_text获取当前数据为空')
            else:
                ...

        self.text += s

        # print(self.text)
        file_path = os.path.join("data", "post_require.txt")
        with open(file_path, "w+", encoding="utf-8") as f:
            f.write(self.text)

    def post_desc_counter(self):
        """ 职位描述统计 """
        # import thulac
        file_path = os.path.join("data", "post_require.txt")
        post = open(file_path, "r", encoding="utf-8").read()
        # 使用 thulac 分词
        # thu = thulac.thulac(seg_only=True)
        # thu.cut(post, text=True)

        # 使用 jieba 分词
        file_path = os.path.join("data", "user_dict.txt")
        jieba.load_userdict(file_path)
        seg_list = jieba.cut(post, cut_all=False)
        counter = dict()
        for seg in seg_list:
            counter[seg] = counter.get(seg, 1) + 1
        counter_sort = sorted(counter.items(), key=lambda value: value[1], reverse=True)
        # pprint(counter_sort)
        file_path = os.path.join("data", "post_pre_desc_counter.csv")
        with open(file_path, "w+", encoding="utf-8") as f:
            f_csv = csv.writer(f)
            f_csv.writerows(counter_sort)

    def post_counter(self):
        """ 职位统计 """
        lst = [c.get('post') for c in self.company]
        counter = Counter(lst)
        counter_most = counter.most_common()
        # pprint(counter_most)
        file_path = os.path.join("data", "post_pre_counter.csv")
        with open(file_path, "w+", encoding="utf-8") as f:
            f_csv = csv.writer(f)
            f_csv.writerows(counter_most)

    def post_salary_locate(self, isOpenPie):
        """饼图: 招聘大概信息，职位，薪酬以及工作地点 """
        lst = []

        bj = 0
        sh = 0
        gz = 0
        sz = 0
        for c in self.company:
            lst.append((c.get('salary'), c.get('post'), c.get('locate')))
            if c.get('locate') in "北京":
                bj += 1
            elif c.get('locate') in "上海":
                sh += 1
            elif c.get('locate') in "广州":
                gz += 1
            elif c.get('locate') in "深圳":
                sz += 1

        if isOpenPie:
            # 设置饼图数据
            infos = [bj, sh, gz, sz]
            pic_package.draw_pie(self.keyworld, infos)

        # pprint(lst)
        file_path = os.path.join("data", "post_salary_locate.csv")
        with open(file_path, "w+", encoding="utf-8") as f:
            f_csv = csv.writer(f)
            f_csv.writerows(lst)

    def post_salary(self):
        """ 薪酬数据统一处理 """
        mouth = []
        year = []
        thouand = []
        file_path = os.path.join("data", "post_salary_locate.csv")
        with open(file_path, "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                if "万/月" in row[0]:
                    mouth.append((row[0][:-3], row[2], row[1]))
                elif "万/年" in row[0]:
                    year.append((row[0][:-3], row[2], row[1]))
                elif "千/月" in row[0]:
                    thouand.append((row[0][:-3], row[2], row[1]))
        # pprint(mouth)
        calc = []
        for m in mouth:
            s = m[0].split("-")
            calc.append(
                (round((float(s[1]) - float(s[0])) * 0.4 + float(s[0]), 1), m[1], m[2]))
        for y in year:
            s = y[0].split("-")
            calc.append(
                (round(((float(s[1]) - float(s[0])) * 0.4 + float(s[0])) / 12, 1), y[1], y[2]))
        for t in thouand:
            s = t[0].split("-")
            calc.append(
                (round(((float(s[1]) - float(s[0])) * 0.4 + float(s[0])) / 10, 1), t[1], t[2]))
        # pprint(calc)
        file_path = os.path.join("data", "post_salary.csv")
        with open(file_path, "w+", encoding="utf-8") as f:
            f_csv = csv.writer(f)
            f_csv.writerows(calc)

    def post_salary_counter(self, isOpenBar):
        """柱形图: 薪酬统计 """

        # 解析post_salary.csv文件数据
        file_path = os.path.join("data", "post_salary.csv")
        with open(file_path, "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            lst = [row[0] for row in f_csv]
            # 重复频率最高的数据,返回次数
        counter = Counter(lst).most_common()
        # pprint(counter)


        if isOpenBar:
            # 将薪资列表中的原则拆开
            line_x = []
            line_y = []
            for i in counter:
                line_x.append(i[0])
            for i in counter:
                line_y.append(i[1])

            # newLine_x = line_x[0:10]
            # newLine_y = line_y[0:10]
            # print("newLine_x",newLine_x)
            # print("newLine_y",newLine_y)

            # 设置柱形图数据
            pic_package.draw_line(self.keyworld, line_x[0:10], line_y[0:10])

        # 写入新的csv文件
        file_path = os.path.join("data", "post_salary_counter1.csv")
        with open(file_path, "w+", encoding="utf-8") as f:
            f_csv = csv.writer(f)
            f_csv.writerows(counter)

    def world_cloud(self):
        """ 生成词云 """
        counter = {}
        file_path = os.path.join("data", "post_pre_desc_counter.csv")
        with open(file_path, "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                counter[row[0]] = counter.get(row[0], int(row[1]))
                # pprint(counter)
        file_path = os.path.join("font", "msyh.ttf")
        wordcloud = WordCloud(font_path=file_path,
                              max_words=100, height=600, width=1200).generate_from_frequencies(counter)
        plt.imshow(wordcloud)
        plt.axis('off')
        plt.show()
        file_path = os.path.join("images", "worldcloud.jpg")
        wordcloud.to_file(file_path)

    def insert_into_db(self):
        """ 自行创建数据库
            create table jobpost(
                j_salary float(3, 1),
                j_locate text,
                j_post text
            );
        """

        # 连接数据库
        import pymysql
        conn = pymysql.connect(host="localhost",
                               port=3306,
                               user="root",
                               passwd="root",
                               db="51job",
                               charset="utf8")
        cur = conn.cursor()
        file_path = os.path.join("data", "post_salary.csv")
        with open(file_path, "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            sql = "insert into jobpost(j_salary, j_locate, j_post) values(%s, %s, %s)"
            for row in f_csv:
                value = (row[0], row[1], row[2])
                try:
                    cur.execute(sql, value)
                    conn.commit()
                except Exception as e:
                    print(e)
        cur.close()


if __name__ == "__main__":
    spider = JobSpider()
    spider.job_spider()
    # 按需启动

    # 功能1: 获取岗位描述,经验,学历
    spider.post_require()
    # 岗位描述统计
    spider.post_desc_counter()

    # 功能2:  北上广深岗位分布情况 饼图(默认false不打开)
    # spider.post_salary_locate(True)

    # 薪酬数据整理分类,将输入插入数据库
    # spider.post_salary()
    # spider.insert_into_db()

    # 功能3:  薪资情况 线型图/圆柱图(默认False不打开)
    # spider.post_salary_counter(True)

    # 职位统计
    # spider.post_counter()

    # 功能4:  岗位热词 云图
    # spider.world_cloud()
