# CNKI 知网爬虫

这个 Python 脚本利用 Selenium 来爬取 CNKI（中国知网）平台基于关键词搜索的论文信息。该脚本能够浏览搜索界面，提取并保存所找到的论文信息。

## 特点

- 根据指定关键词在 CNKI 进行论文搜索。
- 提取信息包括标题、作者、摘要、出版详情等。
- 支持多线程以提高检索速度。
- 将提取的信息保存到指定文件中（在这种情况下是一个 TSV 文件）。
- 异常处理以确保稳健性。

## 讲述

详见[知乎](https://zhuanlan.zhihu.com/p/670809708)或[博客](https://blog.wangzixi.top/2023/12/06/43/)。

## 使用方法

### 1. 环境设置

确保您已经完成以下步骤：

- 安装 Python 3.x 版本。
- 安装 Selenium 库：`pip install selenium`
- 下载并配置适当的 WebDriver。代码示例使用了 Edge WebDriver。
    - 下载 Edge WebDriver：[Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
    - 双击 WebDriver.exe 完成安装

### 2. 代码自定义

使用文本编辑器打开 `cnki_crawler.py` 文件，并根据需要进行以下操作：

- 修改 `keyword` 变量为您感兴趣的关键词，例如 `keyword = "青少年抑郁"`。
- 可选：根据您的需求修改 `papers_need` 变量，设置所需获取的论文数量。


### 3. 运行爬虫

在命令行中执行以下命令来运行爬虫：

```bash
python CNKI_spider_paralle.py
```

脚本将打开一个 Edge 浏览器窗口并开始自动执行搜索并爬取论文信息的操作。请耐心等待脚本执行完毕。

### 4. 结果查看

爬取的结果将保存在名为 `CNKI_关键词.tsv` 的 TSV 文件中（例如 `CNKI_青少年抑郁.tsv`）。您可以使用文本编辑器或Excel打开该文件查看爬取的论文信息。

## 注意事项

- 该脚本配置了 Edge WebDriver，但可以根据需要更改 WebDriver 配置以适用于其他浏览器。
- 确保遵守 CNKI 的服务条款，并避免对其服务器进行过多请求。

## 参考

- Python爬虫实战(5) | 爬取知网文献信息（已优化代码） https://zhuanlan.zhihu.com/p/599579339
- 知网爬虫--根据【关键词】获取文献信息 https://zhuanlan.zhihu.com/p/663793038
