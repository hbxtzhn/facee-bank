---
id: q_01M6ZYJ3Y11V6SFPEYHF98FM9B
title: JSON 序列化怎么用（如 Jackson）？
type: coding
difficulty: easy
importance: 1
category: java
tags: [serialization, reflection]
prerequisites: [q_01M6XBNXGSEB1GY352GJHDQCVF]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Jackson 里用 ObjectMapper：writeValueAsString 把对象转成 JSON 字符串，readValue 把 JSON 字符串还原成对象。

## 要点
- [kp1|3] ObjectMapper 是 Jackson 的入口类，负责对象与 JSON 互转
- [kp2|3] 对象转 JSON 用 writeValueAsString，JSON 转对象用 readValue(json, 类.class)
- [kp3|2] Jackson 通过反射读写 getter/setter 和字段，类需要无参构造器
- [kp4] ObjectMapper 创建开销较大，应当复用同一个实例
- [kp5] JSON 里有类里没有的字段默认会报错，可以配置忽略

## 详解
### 先搞懂：一位翻译官
Java 对象和 JSON 文本是两种语言，ObjectMapper 就像翻译官：你给它一个对象，它翻译成 JSON 文本；给它 JSON 文本和目标类型，它翻成对象。

做项目时，接口收发 JSON、把对象存进缓存，常常就靠它（Spring MVC 默认也使用 Jackson）。

后文术语：
- **ObjectMapper**：Jackson 里的翻译官，所有转换都由它执行。
- **反射**：程序运行时读取类的属性和方法，Jackson 靠它知道对象里有哪些字段。

### 对象转 JSON
调用 `mapper.writeValueAsString(obj)`，返回 JSON 字符串。Jackson 默认按 getter 方法（或公开字段）来取值，字段名就是 JSON 的 key。

### JSON 转对象
调用 `mapper.readValue(json, User.class)`。Jackson 先用无参构造器创建对象，再通过 setter 或字段把值填进去。所以类通常需要一个无参构造器，并且有 setter（或者用注解另行指定）。

### 几个常用配置
- JSON 里有类中没有的字段时，默认会抛异常。想忽略可以关闭 `FAIL_ON_UNKNOWN_PROPERTIES`，或在类上加 `@JsonIgnoreProperties(ignoreUnknown = true)`。
- 想改字段在 JSON 里的名字，用 `@JsonProperty`；想不输出某个字段，用 `@JsonIgnore`。
- 泛型集合（如 `List<User>`）要用 `TypeReference` 告诉 Jackson 具体类型，因为运行时泛型信息被擦除了。

## 示例
```java
ObjectMapper mapper = new ObjectMapper(); // 复用同一个实例

String json = mapper.writeValueAsString(user); // {"name":"Tom","age":20}
User u = mapper.readValue(json, User.class);

List<User> list = mapper.readValue(jsonArray, new TypeReference<List<User>>() {});
```

## 易错点
- 每次转换都 new 一个 ObjectMapper；应复用，它是线程安全的前提是不要在使用中途修改配置
- 反序列化的类没有无参构造器，导致报错
- 直接 `readValue(json, List.class)` 以为得到 `List<User>`；元素其实是 Map，要用 `TypeReference`

## 追问
### [f1] JSON 中有未知字段会怎样？
默认抛 UnrecognizedPropertyException。可以关闭 FAIL_ON_UNKNOWN_PROPERTIES，或在类上加 @JsonIgnoreProperties(ignoreUnknown = true)。
