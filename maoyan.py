import requests
import re
import os
from fontTools.ttLib import TTFont


class MaoYan(object):
    def __init__(self):
        self.url = 'http://maoyan.com/films/1198214'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }

    # 发送请求获得响应
    def get_html(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content

    # 创建 self.font 属性
    def create_font(self, font_file):
        # 列出已下载文件
        file_list = os.listdir('./fonts')
        # 判断是否已下载
        if font_file not in file_list:
            # 未下载则下载新库
            print('不在字体库中, 下载:', font_file)
            url = 'http://vfile.meituan.net/colorstone/' + font_file
            new_file = self.get_html(url)
            with open('./fonts/' + font_file, 'wb') as f:
                f.write(new_file)

        # 打开字体文件，创建 self.font属性
        self.font = TTFont('./fonts/' + font_file)

    # 把获取到的数据用字体对应起来，得到真实数据
    def modify_data(self, data):
        # 获取 GlyphOrder 节点
        gly_list = self.font.getGlyphOrder()
        # 前两个不是需要的值，截掉
        gly_list = gly_list[2:]
        # 枚举, number是下标，正好对应真实的数字，gly是乱码
        for number, gly in enumerate(gly_list):
            # 把 gly 改成网页中的格式
            gly = gly.replace('uni', '&#x').lower() + ';'
            # 如果 gly 在字符串中，用对应数字替换
            if gly in data:
                data = data.replace(gly, str(number))
        # 返回替换后的字符串
        return data

    def start_crawl(self):
        html = self.get_html(self.url).decode('utf-8')

        # 正则匹配字体文件
        font_file = re.findall(r'vfile\.meituan\.net\/colorstone\/(\w+\.woff)', html)[0]
        self.create_font(font_file)

        # 正则匹配星级
        star = re.findall(r'<span class="index-left info-num ">\s+<span class="stonefont">(.*?)</span>\s+</span>', html)[0]
        star = self.modify_data(star)

        # 正则匹配评论的人数
        people = ''.join(re.findall(r'''<span class='score-num'><span class="stonefont">(.*?万)</span>(人评分)</span>''', html)[0])
        people = self.modify_data(people)

        # 正则匹配累计票房
        ticket_number = ''.join(re.findall(r'''<span class="stonefont">(.*?)</span><span class="unit">(亿)</span>''', html)[0])
        ticket_number = self.modify_data(ticket_number)

        print('用户评分: %s 星' % star)
        print('评分人数: %s' % people)
        print('累计票房: %s' % ticket_number)


if __name__ == '__main__':
    maoyan = MaoYan()
    maoyan.start_crawl()
