import scrapy
from scrapy import Request, FormRequest
from scrapy.crawler import CrawlerProcess

class AmazonSpider(scrapy.Spider):
    name = "amazon_spider"
    start_urls = [
        'https://www.amazon.com/gp/bestsellers/climate-pledge/21377129011/ref=pd_zg_hrsr_climate-pledge',
    ]

    def parse(self, response):
        # 在这里编写解析页面的逻辑
        # 这里暂时不需要解析页面，直接发送请求模拟点击和输入
        yield FormRequest.from_response(
            response,
            formid='glow-ingress-line2',
            formdata={'address': '90001'},  # 输入指定的 zip code
            callback=self.after_submit
        )

    def after_submit(self, response):
        # 在这里编写提交后的处理逻辑，比如解析结果或者执行下一步操作
        pass

if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'ROBOTSTXT_OBEY': False  # 忽略 robots.txt 规则
    })
    process.crawl(AmazonSpider)
    process.start()  # the script will block here until the crawling is finished
