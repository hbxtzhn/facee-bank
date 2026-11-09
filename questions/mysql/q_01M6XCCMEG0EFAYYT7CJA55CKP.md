---
id: q_01M6XCCMEG0EFAYYT7CJA55CKP
title: 什么是子查询，怎么写？
type: concept
difficulty: easy
importance: 1
category: mysql
tags: [sql-basics]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
子查询是嵌套在另一条 SQL 里的 SELECT，外层语句用它的结果继续查询。它可以写在 `WHERE`、`FROM` 或 `SELECT` 列表中。

## 要点
- [kp1|3] 子查询是写在括号里的 SELECT，嵌在另一条 SQL 内部
- [kp2|3] `WHERE` 里的子查询常配合 `IN`、`EXISTS` 或比较符使用
- [kp3|2] `FROM` 里的子查询把结果当成一张临时表，必须起别名
- [kp4] `SELECT` 列表里的子查询每行返回一个值，要保证只返回一列一行

## 详解
### 先搞懂：先问第一个问题，再用答案问第二个
问「比平均工资高的员工有哪些」，其实是两个问题：先算出平均工资，再找出比它高的人。子查询就是把第一个问题嵌进第二个问题里，一条 SQL 就能解决。

后文用到的术语：

- **外层查询**：包住子查询的那条 SQL。
- **子查询**：写在括号里的内层 SELECT。
- **派生表**：`FROM` 里子查询产生的临时结果，当成表来用。

### 位置一：WHERE 里的子查询
最常见。用子查询的结果作为过滤条件：

```sql
-- 查工资高于平均工资的员工
SELECT name, salary FROM employee
WHERE salary > (SELECT AVG(salary) FROM employee);

-- 查有订单的用户
SELECT name FROM user
WHERE id IN (SELECT user_id FROM orders);
```

子查询返回单个值时，可以用 `>`、`=` 等比较符；返回多行时，用 `IN` 或 `EXISTS`。

### 位置二：FROM 里的子查询
把子查询的结果当作一张临时表，再对它查询：

```sql
SELECT t.dept_id, t.avg_salary
FROM (
    SELECT dept_id, AVG(salary) AS avg_salary
    FROM employee GROUP BY dept_id
) t
WHERE t.avg_salary > 10000;
```

这里的子查询必须起一个别名（例中的 `t`），否则会报错。

### 位置三：SELECT 列表里的子查询
每一行外层结果，都会带上一个子查询算出的值：

```sql
SELECT u.name,
       (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_cnt
FROM user u;
```

这种子查询每次只能返回一列一行，否则会报错。

### 关联子查询和非关联子查询
- **非关联子查询**：不依赖外层，自己就能独立运行，如上面的求平均工资；
- **关联子查询**：引用了外层的列，如上面 `o.user_id = u.id`，逻辑上外层每一行都要执行一次。

后者容易有性能问题，题库里有专门的题讲怎么优化。

## 示例
```sql
-- 查下单金额最高的订单所属的用户
SELECT name FROM user
WHERE id = (
    SELECT user_id FROM orders
    ORDER BY amount DESC
    LIMIT 1
);
```

## 易错点
- 子查询返回多行，却用了 `=` 比较；会报错，应该改用 `IN`
- `FROM` 里的子查询忘了起别名；MySQL 会报错
- `SELECT` 列表里的子查询返回了多行或多列；必须是一行一列

## 追问
### [f1] IN 和 EXISTS 有什么区别？
`IN` 先算出子查询的结果集，再判断外层的值是否在其中；`EXISTS` 对外层每一行检查子查询是否存在匹配行。写法不同，优化器常把它们改写成相近的执行方式，要用 `EXPLAIN` 验证。
