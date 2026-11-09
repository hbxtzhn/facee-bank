---
id: q_01M6XCBQMYDBPC21HJ1B0Z8D6Y
title: 多对多和多对一关联在 MyBatis 里怎么映射？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [association-mapping]
prerequisites: [q_01M6XCBQ46R9NFPEB69ZYS5SKG]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 3 文档：Mapper XML - Advanced Result Maps（association / collection）", url: "https://mybatis.org/mybatis-3/sqlmap-xml.html" }
estimatedMinutes: 3
---

## 一句话
多对一和一对一一样用 `<association>`，多对多拆成两个一对多，用 `<collection>` 加中间表映射，思路都和前两种一致。

## 要点
- [kp1|3] 多对一：多的一方实体里放一个对象，用 `<association>`
- [kp2|3] 多对多：两边实体各放对方的集合，用 `<collection>`
- [kp3|2] 多对多在数据库里靠中间表连接，查询要联三张表
- [kp4] 选标签只看属性是单个对象还是集合，和表怎么连无关

## 详解
### 先搞懂：从哪一边看，决定用哪个标签
文章和作者：一个作者有很多文章。从文章看作者，是多对一，因为多篇文章对应一个作者。从作者看文章，是一对多。

学生和课程：一个学生选多门课，一门课有多个学生，这是多对多。

选标签的办法只有一条：看你要装进去的那个属性，是一个对象，还是一个集合。

后文用到的术语：
- **中间表**：多对多关系在数据库里要多建一张表，只存两边的 id。

### 多对一：和一对一写法相同
文章实体里放一个 `Author author`，resultMap 里用 `<association property="author" javaType="Author">`。联表查询时，多篇文章的作者列重复，每篇文章各创建一个作者对象，这没有问题。

### 多对多：用 collection，两边各一个
学生实体里放 `List<Course> courses`，课程实体里放 `List<Student> students`。你从哪一边查，就在那一边的 resultMap 里写 `<collection>`。

查询 SQL 要联三张表：学生表、中间表、课程表。结果每行是一个「学生加一门课」，MyBatis 按学生的 `<id>` 合并，把课程追加进列表。

```java
public class Student {
    private Long id;
    private String name;
    private List<Course> courses;
}
```

### 为什么说思路一致
不管是几对几，MyBatis 只做一件事：把联表查出来的一行行数据，按 `<id>` 归并，再按标签把子对象装进父对象。对象怎么装由标签决定，数据库表怎么连由你写的 SQL 决定。

### 进阶：双向关联要小心（基础薄弱可先跳过）
学生里有课程、课程里又有学生，两边都装满会变成循环引用。转 JSON 时可能死循环，所以通常只在一个方向映射，另一方向需要时再单独查。

## 示例
```xml
<resultMap id="studentMap" type="Student">
  <id property="id" column="id"/>
  <result property="name" column="name"/>
  <collection property="courses" ofType="Course">
    <id property="id" column="course_id"/>
    <result property="title" column="title"/>
  </collection>
</resultMap>

<select id="getStudent" resultMap="studentMap">
  select s.id, s.name, c.id as course_id, c.title
  from student s
  left join student_course sc on sc.student_id = s.id
  left join course c on c.id = sc.course_id
  where s.id = #{id}
</select>
```

## 易错点
- 以为多对多要写新标签；其实还是 `<collection>`，只是 SQL 多联一张中间表
- 两边实体互相持有集合并直接序列化；会出现循环引用
- 联多张表却不起别名；同名的 `id` 列会互相覆盖

## 追问
### [f1] 多对一查询时，同一个作者会创建几个对象？
联表查询里每篇文章各自带一份作者列，通常每篇文章各创建一个作者对象，内容相同但不是同一个引用。
