## 🎯 Purpose Recap

The DSL defines **validation rules** to declaratively inspect, compute, and validate XML data, using:

- Expressions for computations
    
- Optional dynamic XPath expressions referencing prior computations
    

---

## 🧩 1️⃣ Document Structure

Top-level object:

```json
{
  "validationSettings": [ ... ]
}
```

---

## 🟢 2️⃣ Validation Rule Structure

Each rule has:

|Field|Type|Required|Description|
|---|---|---|---|
|`id`|string|✅|Unique identifier|
|`description`|string|✅|Human-readable explanation|
|`type`|string|✅|One of: `existence`, `pattern`, `range`, `comparison`, `computedComparison`|
|`severity`|string (enum)|✅|`error`, `warning`, `info`|
|`conditions`|array of conditions|optional|Preconditions|
|`expression`|object|depends|**Expression to compute** (used for `computedComparison`)|
|Additional fields|varies by `type`|depends|See below|

---

## 🟢 3️⃣ Expression Node Structure

Expressions are **recursive trees**. Each node has:

|Field|Type|Description|
|---|---|---|
|`op`|string|Operation name (e.g., `count`, `sum`, `add`, `value`)|
|`args`|array|Arguments (array of expressions or literals)|
|`xpath`|string|XPath expression (used by operations like `count`)|
|`xpathExpression`|object|Expression producing XPath string dynamically|
|`value`|number or string|Literal value (for `literal` op)|
|`dataType`|string|Optional (`integer`, `decimal`, `date`, `string`)|

---

✅ **Important:**  
If an operation uses `xpathExpression`, your interpreter **must evaluate this expression first** to get the XPath query string.

---

## 🟢 4️⃣ Supported Operations (`op`)

You can define and expand operators. Here are **common ones**:

|`op`|Description|
|---|---|
|`count`|Count nodes matching `xpath` or `xpathExpression`|
|`sum`|Sum numeric values of nodes|
|`average`|Average numeric values|
|`value`|Get a scalar node value|
|`literal`|Literal constant|
|`add`|Sum arguments|
|`subtract`|Subtract arguments|
|`multiply`|Multiply arguments|
|`divide`|Divide arguments|
|`if`|Conditional: if arg[0] then arg[1] else arg[2]|
|`and`|Logical AND|
|`or`|Logical OR|
|`not`|Logical NOT|
|`concat`|String concatenation|

✅ You can extend this list as needed.

---

## 🟢 5️⃣ Conditions

Same as before—conditions control **when a rule applies**:

|Field|Type|Description|
|---|---|---|
|`type`|string|`exists`, `attributeEquals`|
|`xpath`|string|XPath query|
|`attribute`|string|For `attributeEquals`|
|`value`|string|For `attributeEquals`|

---

## 🟢 6️⃣ ComputedComparison

A `computedComparison` rule compares **two expressions**:

```json
{
  "comparison": {
    "operator": "==",
    "leftExpression": { ...expression... },
    "rightExpression": { ...expression... }
  }
}
```

✅ You can also support `between` operators if needed (with `lowerExpression` and `upperExpression`).

---

## 🟢 7️⃣ Example Rule with Dynamic XPath

Here’s an example:

```json
{
  "id": "CountItemsWithDynamicType",
  "description": "Count Items where type equals Category",
  "type": "computedComparison",
  "severity": "error",
  "comparison": {
    "operator": "==",
    "leftExpression": {
      "op": "count",
      "xpathExpression": {
        "op": "concat",
        "args": [
          "/Orders/Order/Items/Item[@type='",
          {
            "op": "value",
            "xpath": "/Orders/Order/@Category"
          },
          "']"
        ]
      }
    },
    "rightExpression": {
      "op": "literal",
      "value": 5
    }
  }
}
```

✅ Here:

- The `xpathExpression` _first_ resolves to a string like:
    
    ```
    /Orders/Order/Items/Item[@type='Electronics']
    ```
    
- Then `count` applies.
    

---

✅ **This design allows arbitrary nesting, dynamic XPath, and full expressions.**
