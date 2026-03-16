---
name: crm-customer-import
description: CRM 客户画像搜索与批量导入技能。只要用户提到以下任何一项就必须使用此技能：找客户、搜客户、搜索客户、客户画像、潜在客户、目标客户、客户列表、录入CRM、导入客户、批量导入、添加客户、找一批xx客户、xx地区的客户、xx行业的客户。当用户说「帮我找一批日本客户」「有没有做酒店的客户」「把这些录入系统」「导入CRM」「找年采购额大的客户」等类似表达时，立即使用此技能。即使用户没有明确说「CRM」或「画像」，只要涉及寻找、搜索、导入客户的意图，都要使用此技能。
---

# CRM 客户画像搜索与批量导入

通过结构化条件搜索酒旅行业的潜在 B2B 客户，确认后批量导入 CRM 系统。

## 核心流程

```
1. 用户描述画像 → 2. 你解析为结构化参数 → 3. 调用搜索 → 4. 展示列表 → 5. 用户确认 → 6. 批量导入
```

## 业务背景（重要！）

本公司是 **酒旅行业 B2B 服务商**，搜索的目标客户是：
- **行业**：酒店(hotel)、旅游(travel/tourism)、酒旅(hospitality)、OTA、旅行社(travel agency)
- **业务类型**：B2B 批发、分销、代理
- **目标联系人**：采购决策者、商务合作负责人

在用户未明确指定行业时，**默认添加酒旅 B2B 相关关键词**。

## 工具调用说明（重要！必须遵守）

`search_customer_profile` 和 `batch_import_customer` 是已通过 **OpenClaw MCP 集成**注册好的工具，可以**直接调用**。

**严禁以下行为：**
- ❌ 不要检查本地端口（如 9026）是否有服务在运行
- ❌ 不要尝试通过 HTTP 请求访问任何本地地址
- ❌ 不要查找本地脚本、Go 程序、配置文件来启动服务
- ❌ 不要因为找不到本地服务而报错或放弃

**正确做法：**
- ✅ 解析用户意图为结构化参数
- ✅ 直接调用 MCP 工具 `search_customer_profile` 或 `batch_import_customer`
- ✅ 如果工具返回错误，直接告知用户，不要尝试绕过

---

## 可用工具

### search_customer_profile

通过结构化条件搜索潜在客户，自动富化联系方式。

**参数（全部可选，但至少提供 1 个筛选条件）：**

| 参数 | 类型 | 说明 |
|------|------|------|
| q_keywords | string | 搜索关键词，多个用空格分隔。**默认应包含酒旅行业词** |
| person_titles | string[] | 职位过滤，如 `["Sales Manager", "Business Development"]` |
| person_locations | string[] | 人员所在地，如 `["Japan", "California"]` |
| organization_locations | string[] | 公司总部所在地，如 `["Tokyo", "Singapore"]` |
| person_seniorities | string[] | 职级，可选值: `owner`, `founder`, `c_suite`, `partner`, `vp`, `head`, `director`, `manager`, `senior`, `entry` |
| contact_email_status | string[] | 邮箱状态，默认 `["verified"]` |
| organization_num_employees_ranges | string[] | 员工数范围，如 `["50,200"]` |
| revenue_range_min | int | 公司最低年营收（美元） |
| revenue_range_max | int | 公司最高年营收（美元） |
| per_page | int | 每页数量，1-100，默认 10 |
| page | int | 页码，从 1 开始 |

**返回：** 客户列表（公司名称、联系人姓名、邮箱、电话、区号、国家、地址、备注）

### batch_import_customer

将客户批量导入 CRM 作为潜在客户。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| customers | array | 是 | 客户列表，从 search_customer_profile 返回的结果中获取 |

每个客户包含：
- `name`: 公司名称（必填）
- `contact_name`: 联系人姓名（必填）
- `contact_email`: 联系人邮箱（必填）
- `contact_phone`: 联系人电话（必填）
- `contact_phone_prefix`: 电话区号（可选）
- `country_code`: 国家编码如 US/JP/CN（可选）
- `address`: 地址（可选）
- `remark`: 备注（可选）

**返回：** 成功数、失败数、失败明细

---

## 参数解析指南（你必须遵守）

当用户用自然语言描述画像时，你需要将其拆解为结构化参数。以下是解析规则：

### 1. 关键词 (q_keywords)

用户提到的行业、业务模式等**无法映射到其他结构化字段**的描述，放入 q_keywords。

**默认规则：** 若用户未指定行业，q_keywords 至少包含 `hotel travel hospitality B2B`。

| 用户表达 | q_keywords |
|----------|-----------|
| 酒店客户 | `hotel hospitality B2B` |
| 旅游行业 | `travel tourism B2B` |
| OTA 客户 | `OTA online travel agency B2B` |
| 做酒店批发的 | `hotel wholesale B2B distribution` |
| （未提及行业） | `hotel travel hospitality B2B` |

### 2. 地区 → person_locations 或 organization_locations

地区描述优先映射为 `organization_locations`（按公司总部所在地搜索），如果用户明确说"人在xx"则用 `person_locations`。

| 用户表达 | 参数 | 值 |
|----------|------|-----|
| 日本客户 | organization_locations | `["Japan"]` |
| 东南亚地区 | organization_locations | `["Singapore", "Thailand", "Vietnam", "Indonesia", "Malaysia", "Philippines"]` |
| 欧洲客户 | organization_locations | `["United Kingdom", "Germany", "France", "Spain", "Italy", "Netherlands"]` |
| 美国西海岸 | organization_locations | `["California", "Oregon", "Washington"]` |
| 中东客户 | organization_locations | `["United Arab Emirates", "Saudi Arabia"]` |

### 3. 职位/角色 → person_titles + person_seniorities

| 用户表达 | person_titles | person_seniorities |
|----------|--------------|-------------------|
| 采购负责人 | `["Purchasing Manager", "Procurement Director", "Buyer"]` | `["manager", "director", "head"]` |
| 商务合作 | `["Business Development", "Partnership Manager", "Sales Manager"]` | `["manager", "director"]` |
| 老板/决策者 | `["CEO", "General Manager", "Owner"]` | `["owner", "founder", "c_suite"]` |
| 销售总监 | `["Sales Director", "VP of Sales"]` | `["director", "vp"]` |
| （未指定）| 不填 | `["manager", "director", "vp", "head", "c_suite"]` |

### 4. 规模/营收 → 员工数或营收范围

| 用户表达 | 参数 | 值 |
|----------|------|-----|
| 大型企业 | organization_num_employees_ranges | `["500,10000"]` |
| 中小企业 | organization_num_employees_ranges | `["10,500"]` |
| 年营收超过100万美元 | revenue_range_min | `1000000` |
| 年营收500万以上 | revenue_range_min | `5000000` |

### 5. 数量控制

| 用户表达 | per_page |
|----------|---------|
| 找5个 | 5 |
| 找一批 / 帮我找些 | 10 |
| 多找一些 | 25 |
| 找50个 | 50 |

---

## 使用指南

### 步骤 1：理解并解析

收到用户的画像描述后，按上述规则解析为结构化参数。**不要直接把中文传给 q_keywords**，必须翻译为英文关键词。

### 步骤 2：调用搜索并展示结果

调用 `search_customer_profile` 后，用以下格式展示：

```
根据您的需求，搜索条件：
- 关键词：{q_keywords}
- 地区：{locations}
- 职级：{seniorities}

共找到 {total} 条匹配记录，本次获取 {count} 条：

1. **{公司名称}**
   - 联系人：{contact_name}
   - 职位/行业：{remark}
   - 邮箱：{contact_email}
   - 电话：{contact_phone_prefix} {contact_phone}
   - 地区：{country_code}
   - 地址：{address}

2. ...

是否要将这些客户录入 CRM 系统？也可以输入「下一页」查看更多。
```

### 步骤 3：确认导入

用户回复肯定词（「是」「好的」「录入」「导入」「确认」）时，调用 `batch_import_customer`，将 search 返回的客户列表**原样**传入。

### 步骤 4：反馈结果

```
导入完成！成功 {success} 条，失败 {fail} 条。
{如有失败，列出失败明细及原因}
```

---

## 示例对话

### 示例 1：基础搜索

**用户**：帮我找一批日本地区的酒店客户

**你的解析**：
- q_keywords: `"hotel hospitality B2B"`
- organization_locations: `["Japan"]`
- person_seniorities: `["manager", "director", "vp", "head", "c_suite"]`
- contact_email_status: `["verified"]`
- per_page: `10`

**调用**：`search_customer_profile(q_keywords="hotel hospitality B2B", organization_locations=["Japan"], person_seniorities=["manager", "director", "vp", "head", "c_suite"], per_page=10)`

### 示例 2：带角色条件

**用户**：找东南亚做酒店批发的采购负责人，要大公司的

**你的解析**：
- q_keywords: `"hotel wholesale B2B distribution"`
- organization_locations: `["Singapore", "Thailand", "Vietnam", "Indonesia", "Malaysia", "Philippines"]`
- person_titles: `["Purchasing Manager", "Procurement Director", "Buyer", "Sourcing Manager"]`
- person_seniorities: `["manager", "director", "head"]`
- organization_num_employees_ranges: `["500,10000"]`
- per_page: `10`

### 示例 3：翻页

**用户**：下一页

**你的操作**：使用与上次相同的参数，page 加 1

### 示例 4：选择性导入

**用户**：第 1、3、5 个录入 CRM

**你的操作**：从搜索结果中提取第 1、3、5 条，调用 `batch_import_customer`

---

## 注意事项

1. **直接调用 MCP 工具**：`search_customer_profile` 和 `batch_import_customer` 已注册为 MCP 工具，无需检查端口或启动任何本地服务，直接调用即可
2. **关键词必须英文**：q_keywords 必须是英文，不能传中文
2. **默认行业词**：用户未提行业时默认加 `hotel travel hospitality B2B`
3. **默认职级**：用户未提职位/角色时默认加中高层筛选
4. **默认邮箱验证**：contact_email_status 默认 `["verified"]`
5. **邮箱去重**：导入时系统按联系邮箱去重，已存在的邮箱会导入失败
6. **必填字段**：导入时公司名称、联系人、邮箱、电话为必填
7. **每次最多 10 条**：搜索+富化每次最多返回 10 条（受 API 限制），如需更多请翻页
8. **Credits 消耗**：搜索免费，富化联系方式每人消耗 1 Credit
