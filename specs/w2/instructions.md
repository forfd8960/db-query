# Instructions

## Constitution

- 后端使用 Ergonomic Python 风格来编写后端代码，确保代码可读性和一致性。 前端使用 typescript.
- 前后端要有严格的类型标注。
- 使用 pydantic 来定义数据模型.
- 所有后端生成的数据，使用 camelCase 格式。
- 不需要 authentication, 任何用户都可以使用。



## 基本思路

这是一个数据库查询工具，用户可以添加一个 DB URL，然后系统会连接到数据库，获取数据库的 metadata, 然后数据库中的 table, view 的信息会展示在左侧的树形结构中，用户可以点击某个 table/view, 然后右侧会展示该 table/view 的 columns 信息，以及允许用户输入 SQL 查询语句，执行查询后，结果会展示在下方的表格中。
同时用户也可以通过自然语言输入查询需求，系统会将自然语言转换为 SQL 语句，然后执行查询并展示结果。

基本想法

- 数据库连接 URL 和数据库的 metadata 都会存储到 sqlite 中. 我们可以根据 postgres 的功能来查询系统中的表和视图的信息，然后用 LLM 来讲这些信息转换成 json 格式，然后存储到 sqlite 中.这个信息以后可以复用。

- 当用户通过 LLM 来生成 sql 查询时，我们可以把系统中的表和视图的信息，以及 columns 信息，传递给 LLM, 让 LLM 帮助生成 SQL 查询语句.

- 任何输入的 sql 语句都需要经过 sqlparse 来解析，确保语法正确，并且仅包含 select 语句，如果语法不正确，需要给出错误信息。
  - 如何查询不包含 Limit 子句， 则默认添加 limit 1000 子句.
- 输出格式是 json, 前端将其组织成表格，并显示出来。

- 后端使用 Python / fastAPI / sqlglot / openai sdk 来实现
- 前端使用 React / refine 5/  tailwind / ant design 来实现
- sql editor 使用 monaco editor 来实现.
- OpenAI 的 API key 通过环境变量(OPENAI_API_KEY)传递给后端.
- 数据库连接 URL 和 metadata 存储在 sqlite 中, 放在 ./db-query/db_query.db 中.
- 后端 API 需要支持 CORS, 允许所有 origin.

大致的 API 列表如下:

```
  POST /api/v1/databases/  - 添加一个新的数据库连接 URL

  {"url": "postgresql://user:pass@host:port/dbname"}

  GET /api/v1/databases/  - 获取所有的数据库连接 URL 列表

  PUT /api/v1/databases/{db_name}/  - 更新指定的数据库连接 URL

  {"url": "postgresql://user:pass@host:port/dbname"}

  GET /api/v1/databases/{db_name}/metadata/  - 获取指定数据库的 metadata (tables, views, columns)

  POST /api/v1/databases/{db_name}/query/  - 执行 SQL 查询

  {"sql": "SELECT * FROM table_name LIMIT 10"}

  POST /api/v1/databases/{db_name}/nl-query/  - 执行自然语言查询

  {"nl_query": "Get me the first 10 rows from table_name"}
```

## 添加 MySQL 支持

参考 ./backend/ 中的 Postgres 相关实现，添加 MySQL 支持。需要注意 MySQL 的 metadata 查询语句与 Postgres 不同，需要使用 MySQL 的信息模式 (information_schema) 来获取表和列的信息。同时支持自然语言查询功能，确保 MySQL 也能通过 LLM 来生成 SQL 查询语句。目前我本地有一个 `myapp1` 的 MySQL 数据库，可以使用 `mysql -u root -e "SELECT * FROM myapp1.todos;"` 可以查询到数据.


## Code review command

帮我参照 @.github/agents/speckit.specify.agent.md 的结构，think ultra hard, 构建一个对 Python 和 TypeScript 代码进行深度代码审查的命令, 放在 .github/agents 目录下. 主要考虑以下几点:

- 架构设计： 是否考虑 Python 和 TypeScript 的架构设计的最佳实践和设计模式， 是否有清晰的接口设计，是否考虑可扩展性。
- KISS 原则： 代码是否遵循 KISS 原则， 是否有不必要的复杂性， 是否有冗余代码。
- 代码质量： 是否考虑了 DRY, YAGNI, SOLID 等原则， 是否有良好的命名规范， 是否有适当的注释和文档；函数实现行数不超过 150 行; 参数不能超过 6 个。

## 数据导出

在当前功能基础上，增加新的输出导出功能，支持 CSV, JSON, Excel 三种格式的导出。用户在执行 SQL 查询后，可以选择将查询结果导出为上述三种格式之一。后端需要实现相应的导出逻辑，并提供下载链接给前端。前端需要在查询结果展示区域增加导出按钮，用户点击后可以选择导出格式并下载文件。