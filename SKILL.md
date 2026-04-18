---
name: crm-customer-import
description: CRM 客户画像搜索与批量导入技能。只要用户提到以下任意一项就必须使用此技能：找客户、搜客户、搜索客户、客户画像、潜在客户、目标客户、客户列表、录入CRM、导入客户、批量导入、添加客户、找一批xx客户、xx地区的客户、xx行业的客户、酒店客户、酒旅客户、OTA客户、旅行社客户、商旅客户、分销客户、批发客户、TMC、DMC、bedbank、wholesaler、B2B客户。即使用户没有明确说“CRM”或“画像”，只要意图是寻找、筛选、导入潜在客户，都要立即使用此技能。
metadata.openclaw: {"primaryEnv": "user_key.txt", "mcpServer": "http://39.108.114.224:9059"}
---

# CRM 客户画像搜索与批量导入

通过结构化条件搜索酒旅行业与 B2B 场景的潜在客户，确认后批量导入 CRM。

## 核心流程

```text
1. 用户描述目标客户
2. 你将自然语言拆解为 Apollo 可识别的结构化参数
3. 调用 search_customer_profile
4. 展示结果并询问是否导入
5. 用户确认后调用 batch_import_customer
```

## 业务背景（重要）

本公司是 **酒旅行业 B2B 服务商**，核心目标客户主要包括：

- 酒店：hotel, resort, hospitality group, serviced apartment
- 旅游：travel, tourism, tour operator, travel agency
- OTA / 分销：OTA, online travel agency, wholesaler, bedbank, distribution
- 商旅：business travel, corporate travel, TMC
- 地接 / 目的地服务：DMC, destination management

目标联系人优先是：

- 商务合作负责人：Business Development, Partnership, Commercial
- 采购 / 签约负责人：Procurement, Contracting, Sourcing, Supplier
- 酒店收益 / 渠道负责人：Revenue, Distribution, Ecommerce
- 高层决策人：Founder, Owner, CEO, GM, VP, Head, Director

## Apollo 搜索原则（非常重要）

Apollo 这一套接口本质是 **按人搜索**，不是按一句画像描述直接找公司。

正确思路是：

1. 先定义 **公司画像**
2. 再定义 **联系人画像**
3. 最后再补邮箱状态、规模、营收等过滤条件

也就是说，你在构造参数时要优先关注：

- `q_keywords`：行业和业务模式关键词
- `organization_locations`：公司所在区域
- `person_titles`：联系人岗位
- `person_seniorities`：联系人层级

不要把用户原话整句塞给 Apollo。
特别是 `q_keywords`：

- 必须转成英文关键词
- 要短、准、可检索
- 不要传中文
- 不要传长句
- 不要只写一个空泛词如 `B2B`

## 工具调用说明（必须遵守）

`search_customer_profile` 和 `batch_import_customer` 已通过 OpenClaw MCP 集成注册完成，可以直接调用。

错误做法：

- 不要检查本地端口
- 不要尝试本地 HTTP 调试
- 不要因为没有本地服务而放弃

正确做法：

- 直接把用户需求解析为结构化参数
- 调用 `search_customer_profile`
- 搜索结果确认后调用 `batch_import_customer`
- 如果工具返回 `unauthorized`，删除 `{baseDir}/user_key.txt` 并引导用户重新提供 `user_key`

---

## Setup

调用任何工具前，必须先完成用户身份验证。

### Step 1 - User Key

1. 读取 `{baseDir}/user_key.txt`
2. 如果文件不存在或为空，不要调用任何工具，告知用户：
   > "在开始之前，需要先验证你的身份。请前往 https://aauth-170125614655.asia-northeast1.run.app/dashboard 用 Google 账号登录，复制你的 `user_key`（格式：`uk_xxxxxxxx`），然后告诉我。"
3. 如果文件存在且有内容，将其值作为所有工具调用的 `user_key`
4. 如果任意工具返回 `unauthorized`，删除 `{baseDir}/user_key.txt` 并重新执行第 2 步

---

## 可用工具

### search_customer_profile

通过结构化条件搜索潜在客户，并自动富化联系人信息。

参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| user_key | string | 从 `{baseDir}/user_key.txt` 读取 |
| q_keywords | string | 英文关键词，多个词用空格分隔 |
| person_titles | string[] | 联系人岗位 |
| person_locations | string[] | 联系人所在地区 |
| organization_locations | string[] | 公司所在地区，优先使用 |
| person_seniorities | string[] | 联系人层级 |
| contact_email_status | string[] | 邮箱状态 |
| organization_num_employees_ranges | string[] | 公司人数范围 |
| revenue_range_min | int | 最低营收（美元） |
| revenue_range_max | int | 最高营收（美元） |
| per_page | int | 每页数量 |
| page | int | 页码，从 1 开始 |

### batch_import_customer

将搜索结果批量导入 CRM 作为潜在客户。

---

## 参数解析指南（必须遵守）

当用户描述目标客户时，你必须先转成 Apollo 更容易命中的结构化参数。

### 1. 先判断搜索意图属于哪一类

优先把用户需求归到下面某个业务场景：

- 酒店 / 酒店集团
- OTA / 在线旅游平台
- 旅行社 / tour operator
- 分销 / 批发 / wholesaler / bedbank
- 商旅 / corporate travel / TMC
- 地接 / DMC

如果用户没有明确说行业，默认按 **酒旅 B2B 潜客** 搜索。

### 2. q_keywords 规则

`q_keywords` 负责表达行业和业务模式，是最重要的字段之一。

规则：

- 用英文关键词，不用中文
- 2 到 6 个核心词即可
- 优先写行业词 + 业务模式词
- 不要写成长句
- 不要堆过多同义词

推荐映射：

| 用户表达 | q_keywords |
|----------|-----------|
| 酒店客户 | `hotel hospitality resort` |
| 酒店集团 | `hotel hospitality group` |
| OTA 客户 | `ota online travel agency` |
| 旅行社 | `travel agency tour operator` |
| 酒旅分销 / 批发 | `hotel wholesale travel distribution bedbank` |
| 商旅客户 | `business travel corporate travel tmc` |
| 地接 / DMC | `destination management dmc inbound travel` |
| 酒旅 B2B 客户 | `hotel travel hospitality b2b` |
| 未明确行业 | `hotel travel hospitality b2b` |

补充规则：

- 用户提到“日本酒店批发商”这类表达时，`q_keywords` 应包含行业词和模式词，如 `hotel wholesale distribution`
- 用户提到“商旅公司”时，不要只写 `travel`，要优先写 `business travel corporate travel tmc`
- 用户提到“对接酒店资源”“酒店签约”“合同采购”时，要优先补 `hotel`, `distribution`, `contracting`, `supplier`

### 3. 地区规则

默认优先用 `organization_locations`，因为我们通常要找“公司在哪个市场”的客户。

只有在用户明确说“人在某地”“当地负责人”“东京办公室的人”时，才用 `person_locations`。

常用地区映射：

| 用户表达 | 参数 | 值 |
|----------|------|-----|
| 日本客户 | organization_locations | `["Japan"]` |
| 东京客户 | organization_locations | `["Tokyo"]` |
| 东南亚客户 | organization_locations | `["Singapore", "Thailand", "Vietnam", "Indonesia", "Malaysia", "Philippines"]` |
| 欧洲客户 | organization_locations | `["United Kingdom", "Germany", "France", "Spain", "Italy", "Netherlands"]` |
| 中东客户 | organization_locations | `["United Arab Emirates", "Saudi Arabia", "Qatar"]` |
| 美国西海岸 | organization_locations | `["California", "Oregon", "Washington"]` |
| 香港客户 | organization_locations | `["Hong Kong"]` |

### 4. person_titles 规则

在酒旅行业里，不要优先使用过于泛化的岗位，如只写 `Sales Manager`。
优先使用更接近合作、签约、分销、收益管理的岗位。

推荐映射：

| 用户表达 | person_titles |
|----------|---------------|
| 商务合作负责人 | `["Business Development", "Business Development Manager", "Partnership Manager", "Head of Partnerships", "Commercial Director"]` |
| 采购负责人 | `["Procurement Manager", "Purchasing Manager", "Sourcing Manager", "Buyer"]` |
| 签约负责人 | `["Contracting Manager", "Supplier Manager", "Market Manager"]` |
| 酒店渠道 / 收益负责人 | `["Revenue Manager", "Distribution Manager", "Ecommerce Manager"]` |
| 老板 / 决策人 | `["CEO", "Founder", "Owner", "General Manager", "Managing Director"]` |
| 未指定联系人角色 | 可以不填 titles，但要补 seniorities |

细化建议：

- 用户说“对接渠道”“BD”“商务合作”，优先走 `Business Development` / `Partnership`
- 用户说“酒店采购”“合同采购”“资源采购”，优先走 `Procurement` / `Sourcing` / `Buyer`
- 用户说“酒旅签约”“酒店签约”“供应商对接”，优先走 `Contracting Manager` / `Supplier Manager`
- 用户说“酒店收益”“渠道运营”，优先走 `Revenue Manager` / `Distribution Manager`

### 5. person_seniorities 规则

默认不要一开始限制得过死。

推荐策略：

- 未指定角色时，默认：`["manager", "director", "head", "vp"]`
- 明确找老板 / 决策人：`["owner", "founder", "c_suite"]`
- 明确找中层执行负责人：`["manager", "director", "head"]`
- 结果太少时，可以放宽到：`["manager", "director", "head", "vp", "c_suite"]`

### 6. contact_email_status 规则

为了兼顾召回和可导入性，默认使用：

```json
["verified", "likely to engage"]
```

只有在用户明确要求“邮箱质量更高”“只要可直接导入的”时，才收紧为：

```json
["verified"]
```

### 7. 公司规模 / 营收规则

| 用户表达 | 参数 | 值 |
|----------|------|-----|
| 大公司 | organization_num_employees_ranges | `["500,10000"]` |
| 中型公司 | organization_num_employees_ranges | `["50,500"]` |
| 中小企业 | organization_num_employees_ranges | `["10,500"]` |
| 年营收超过 100 万美元 | revenue_range_min | `1000000` |
| 年营收超过 500 万美元 | revenue_range_min | `5000000` |

### 8. 数量规则

当前链路每次最多稳定处理 10 条搜索结果，因此：

- 默认 `per_page=10`
- 用户说“找一批”“多找一些”时，仍优先取 `10`
- 用户说“找 5 个”时用 `5`
- 用户如果要更多，提示可继续查看下一页

不要默认传大于 10 的 `per_page`。

---

## 搜索策略（非常重要）

### 第一轮：先保证命中

默认按下面思路搜索：

- 用行业词 + 业务模式词生成 `q_keywords`
- 用 `organization_locations` 限定区域
- 用更贴近酒旅场景的 `person_titles`
- `person_seniorities` 先不要太严
- `contact_email_status` 默认用 `["verified", "likely to engage"]`

### 第二轮：结果太少时自动放宽

如果第一轮结果为 0，或明显太少（例如少于 3 条），按下面顺序放宽，并重新调用 `search_customer_profile`：

1. 放宽 `person_seniorities`
2. 去掉 `person_titles`，只保留行业词和地区
3. 保留核心行业词，减少过细的业务模式词
4. 如用户区域太窄，可放宽到更大的国家/区域级别

放宽时要遵守：

- 保留用户核心行业意图
- 不要把“酒店客户”放宽成完全无关行业
- 不要随意删除用户明确要求的国家或地区

---

## 使用指南

### 步骤 1：理解并解析

收到用户需求后，先按以下格式在心里完成解析：

- 行业类别
- 区域
- 联系人角色
- 联系人层级
- 公司规模 / 营收
- 是否需要更高邮箱质量

然后把它转成 Apollo 参数。

### 步骤 2：调用搜索并展示结果

调用 `search_customer_profile` 后，用下面格式回答：

```text
根据您的需求，我使用以下条件搜索：
- 关键词：{q_keywords}
- 公司地区：{organization_locations}
- 联系人岗位：{person_titles}
- 联系人层级：{person_seniorities}

共找到 {total} 条匹配记录，本次获取 {count} 条：

1. {公司名称}
   联系人：{contact_name}
   职位/备注：{remark}
   邮箱：{contact_email}
   电话：{contact_phone_prefix} {contact_phone}
   地区：{country_code}
   地址：{address}

是否要将这些客户录入 CRM 系统？也可以输入“下一页”查看更多。
```

### 步骤 3：确认导入

当用户回复“是”“好的”“导入”“录入”“确认”等肯定词时，调用 `batch_import_customer`。

如果用户说“第 1、3、5 个导入”，则只提取对应结果调用导入工具。

### 步骤 4：导入反馈

```text
导入完成！成功 {success} 条，失败 {fail} 条。
如有失败，列出失败明细和原因。
```

---

## 场景模板

### 模板 1：找日本酒店合作负责人

用户表达：

```text
帮我找一批日本酒店客户
```

推荐解析：

- q_keywords: `"hotel hospitality resort"`
- organization_locations: `["Japan"]`
- person_titles: `["Business Development", "Partnership Manager", "Commercial Director", "Revenue Manager", "Distribution Manager"]`
- person_seniorities: `["manager", "director", "head", "vp"]`
- contact_email_status: `["verified", "likely to engage"]`
- per_page: `10`

### 模板 2：找东南亚酒店分销 / 批发客户

用户表达：

```text
找东南亚做酒店批发的客户
```

推荐解析：

- q_keywords: `"hotel wholesale travel distribution bedbank"`
- organization_locations: `["Singapore", "Thailand", "Vietnam", "Indonesia", "Malaysia", "Philippines"]`
- person_titles: `["Contracting Manager", "Supplier Manager", "Market Manager", "Business Development Manager"]`
- person_seniorities: `["manager", "director", "head"]`
- contact_email_status: `["verified", "likely to engage"]`
- per_page: `10`

### 模板 3：找欧洲商旅 / TMC 客户

用户表达：

```text
找欧洲的商旅客户
```

推荐解析：

- q_keywords: `"business travel corporate travel tmc"`
- organization_locations: `["United Kingdom", "Germany", "France", "Spain", "Italy", "Netherlands"]`
- person_titles: `["Head of Partnerships", "Commercial Director", "Business Development Director"]`
- person_seniorities: `["director", "head", "vp"]`
- contact_email_status: `["verified", "likely to engage"]`
- per_page: `10`

### 模板 4：找 OTA / 在线旅游平台客户

用户表达：

```text
有没有做 OTA 的潜在客户
```

推荐解析：

- q_keywords: `"ota online travel agency"`
- person_titles: `["Partnership Manager", "Business Development Manager", "Market Manager", "Commercial Director"]`
- person_seniorities: `["manager", "director", "head"]`
- contact_email_status: `["verified", "likely to engage"]`
- per_page: `10`

### 模板 5：找 DMC / 地接公司客户

用户表达：

```text
帮我找中东地区做地接的客户
```

推荐解析：

- q_keywords: `"destination management dmc inbound travel"`
- organization_locations: `["United Arab Emirates", "Saudi Arabia", "Qatar"]`
- person_titles: `["General Manager", "Business Development Manager", "Partnership Manager"]`
- person_seniorities: `["manager", "director", "head"]`
- contact_email_status: `["verified", "likely to engage"]`
- per_page: `10`

---

## 注意事项

1. 必须直接调用 MCP 工具，不要绕开技能流程
2. `q_keywords` 必须是英文关键词，不是中文句子
3. 默认优先使用 `organization_locations`，不是 `person_locations`
4. 默认优先使用酒旅行业专用岗位，不要只用泛销售岗位
5. 默认邮箱状态建议使用 `["verified", "likely to engage"]`
6. 用户明确要求高质量邮箱时，再收紧成 `["verified"]`
7. 每次默认最多取 10 条，更多结果通过翻页获取
8. 导入时邮箱、联系人、电话、公司名是关键字段，展示结果时要提醒用户注意完整性
