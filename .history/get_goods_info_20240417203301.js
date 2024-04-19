// 初始化一个空字符串，用于存储结果
var divInfo = '';

// 查找所有 class='a-declarative' 的元素
var divElements = document.querySelectorAll('.a-declarative');

// 遍历所有找到的元素
divElements.forEach(function(divElement) {
    // 查找当前元素下属性为 name 或者 data-cy 的子元素
    var nameElements = divElement.querySelectorAll('[name]');
    var dataCyElements = divElement.querySelectorAll('[data-cy]');

    // 遍历所有属性为 name 或者 data-cy 的子元素
    nameElements.forEach(function(nameElement) {
        divInfo += nameElement.textContent.trim();
        // 查找国家：查找当前元素下的所有 i 标签
        var iElements = nameElement.querySelectorAll('i');

        // 遍历所有 i 标签
        iElements.forEach(function(iElement) {
            // 检查 i 标签的 class 值
            var classList = iElement.classList;

            // 如果 class 值包含 "flag-icon-cn"，则国家为中国
            if (classList.contains("flag-icon-cn")) {
                divInfo += '国家: 中国';
            }
            // 如果 class 值包含 "flag-icon-us"，则国家为美国
            else if (classList.contains("flag-icon-us")) {
                divInfo += '国家: 美国';
            }
            // 其他情况，国家为其他
            else {
                divInfo += '国家: 其他';
            }
        });
    });

    // 查找标题
    dataCyElements.forEach(function(dataCyElement) {
        var dataCyAttributeValue = dataCyElement.getAttribute('data-cy');
    
        // 检查 data-cy 属性的值是否为标题
        if (dataCyAttributeValue === 'title-recipe') {
            var h2Elements = dataCyElement.querySelectorAll('h2');
            h2Elements.forEach(function(h2Element) {
                var aElement = h2Element.querySelector('a');
                if (aElement) {
                    divInfo += "标题: " + aElement.textContent.trim()+ "\n";
                }
            });
        }
    });
});