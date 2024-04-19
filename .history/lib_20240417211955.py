def parse_asin(grid_item):
    try:
        # 查找具有data-asin属性的div元素
        div_with_asin = grid_item.find_element_by_xpath(".//div[@data-asin]")
        # 获取data-asin属性值
        asin = div_with_asin.get_attribute("data-asin")
        return asin
    except NoSuchElementException:
        # 没有找到对应的内容，返回空
        return None