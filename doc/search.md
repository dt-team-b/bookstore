## 搜索

#### URL

POST http://[address]/search/search

#### Request

Headers:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

Body:

```json
{
  "search_info": {
    "title": [
      "key word1",
      "key word2",
      "..."
    ],
    "tags": [
      "tags1",
      "tags2",
      "tags3",
      "..."
    ],
    "contents": [
      "key word1",
      "key word2",
      "key word3",
      "..."
    ]
  },
  "store_id": "$store id$",
  "page_id": "$page id$"
}
```

key | 类型 | 描述 | 是否可为空
---|---|---|---
store_id | string | 商铺ID | Y
page_id | int | 页码 | N
search_info | class | 查询信息 | N

search_info类：

key | 类型 | 描述 | 是否可为空
---|---|---|---
title | array | 标题关键词 | Y
tags | array | 标签 | Y
contents | array | 内容关键词 | Y

title,tags,contents的每个元素都是string类型的。其中，tags的元素只能精确匹配，其余两者可以模糊搜索。

#### Response

Status Code:

码 | 描述
--- | ---
200 | 查询成功
5XX | 商铺ID不存在
5XX | 页码不存在

##### Body:

```json
{
  "books": [
    "book_info1",
    "book_info2",
    "book_info3",
    "..."
  ]
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
books | array | 书籍信息，只有返回200时才有效 | N

books的每个元素都是book_info类

book_info类：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
id | string | 书籍ID | N
title | string | 书籍题目 | N
author | string | 作者 | Y
publisher | string | 出版社 | Y
original_title | string | 原书题目 | Y
translator | string | 译者 | Y
pub_year | string | 出版年月 | Y
pages | int | 页数 | Y
price | int | 价格(以分为单位) | N
binding | string | 装帧，精状/平装 | Y
isbn | string | ISBN号 | Y
author_intro | string | 作者简介 | Y
book_intro | string | 书籍简介 | Y
content | string | 样章试读 | Y
tags | array | 标签 | Y
pictures | array | 照片 | Y