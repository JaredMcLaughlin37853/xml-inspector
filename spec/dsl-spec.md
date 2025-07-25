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
|`type`|string|✅|One of: `existence`, `pattern`, `range`, `comparison`, `computedComparison`, `nodeValidation`|
|`severity`|string (enum)|✅|`error`, `warning`, `info`|
|`conditions`|array of conditions|optional|Preconditions|
|`expression`|object|depends|**Expression to compute** (used for `computedComparison`)|
|Additional fields|varies by `type`|depends|See below|

---

## 🟢 3️⃣ Expression Node Structure

Expressions are **recursive trees**. Each node has:

| Field             | Type                       | Description                                                  |
| ----------------- | -------------------------- | ------------------------------------------------------------ |
| `op`              | string                     | Operation name (e.g., `count`, `sum`, `add`, `value`, `map`) |
| `args`            | array                      | Arguments (array of expressions or literals)                 |
| `xpath`           | string                     | XPath expression selecting nodes                             |
| `xpathExpression` | object                     | Expression producing XPath string dynamically                |
| `expression`      | object                     | Expression applied per node (for `map`)                      |
| `value`           | number, string, or boolean | Literal value (for `literal` op)                             |
| `dataType`        | string                     | Optional (`integer`, `decimal`, `date`, `string`)            |


---

✅ **Important:**  
If an operation uses `xpathExpression`, your interpreter **must evaluate this expression first** to get the XPath query string.

---

## 🟢 4️⃣ Supported Operations (`op`)

You can define and expand operators. Here are **common ones**:

| `op`       | Description                                                     |
| ---------- | --------------------------------------------------------------- |
| `count`    | Count nodes matching `xpath` or `xpathExpression`               |
| `sum`      | Sum numeric values of nodes or array                            |
| `average`  | Average numeric values                                          |
| `value`    | Get a scalar node value                                         |
| `literal`  | Literal constant                                                |
| `add`      | Sum arguments                                                   |
| `subtract` | Subtract arguments                                              |
| `multiply` | Multiply arguments                                              |
| `divide`   | Divide arguments                                                |
| `if`       | Conditional: if arg\[0] then arg\[1] else arg\[2]               |
| `and`      | Logical AND                                                     |
| `or`       | Logical OR                                                      |
| `not`      | Logical NOT                                                     |
| `concat`   | String concatenation                                            |
| `==`       | Equality                                                        |
| `!=`       | Inequality                                                      |
| `>`        | Greater than                                                    |
| `<`        | Less than                                                       |
| `>=`       | Greater or equal                                                |
| `<=`       | Less or equal                                                   |
| `map`      | Iterate over nodes and evaluate an expression per node |


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

🟢 8️⃣ Example Use of map
Scenario:
Compute the total value of all <Item> elements as @quantity * @price.

{
  "op": "sum",
  "args": [
    {
      "op": "map",
      "xpath": "/Orders/Order/Items/Item",
      "expression": {
        "op": "multiply",
        "args": [
          { "op": "value", "xpath": "@quantity" },
          { "op": "value", "xpath": "@price" }
        ]
      }
    }
  ]
}

How it works:

map iterates over each <Item>.

For each node, evaluates quantity * price.

Returns an array of results.

sum aggregates the array.

## 🟢 9️⃣ Node Validation

The `nodeValidation` type allows validating multiple nodes individually, producing per-node PASS/FAIL results.

### Syntax

```json
{
  "type": "nodeValidation",
  "nodesXpath": "//XPath/to/select/nodes",
  "nodeValueExpression": { /* expression to extract value from each node */ },
  "expectedValueExpression": { /* optional: expression to get expected value per node */ },
  "value": "constant_expected_value", // optional: use instead of expectedValueExpression
  "operator": "==|!=|>|<|>=|<="
}
```

### Fields

|Field|Type|Required|Description|
|---|---|---|---|
|`nodesXpath`|string|✅|XPath to select nodes for validation|
|`nodeValueExpression`|expression|✅|Expression to extract value from each node|
|`expectedValueExpression`|expression|⚫|Expression to compute expected value per node|
|`value`|literal|⚫|Fixed expected value (alternative to `expectedValueExpression`)|
|`operator`|string|⚫|Comparison operator (defaults to `==`)|

### Simple Example

```json
{
  "id": "validate_each_dca_record",
  "description": "Validate each DCA record individually",
  "type": "nodeValidation",
  "severity": "error",
  "nodesXpath": "//B023_CFG/Record", 
  "nodeValueExpression": {
    "op": "value",
    "xpath": "@First_x0020_Device_x0020_Entry",
    "dataType": "integer"
  },
  "value": 0,
  "operator": ">="
}
```

### Complex Mapping Example

This example shows complex node validation with mapping between related XML nodes:

```json
{
  "id": "count_analog_input_16_per_dca_record",
  "description": "For each DCA record, count Analog Input 16 points using mapping",
  "type": "nodeValidation",
  "severity": "info",
  "nodesXpath": "//B023_CFG/Record",
  "nodeValueExpression": {
    "op": "sum",
    "args": [
      {
        "op": "map",
        "xpathExpression": {
          "op": "concat",
          "args": [
            "//B023_DEV/Record[position() >= ",
            {
              "op": "add",
              "args": [
                {"op": "value", "xpath": "@First_x0020_Device_x0020_Entry", "dataType": "integer"},
                {"op": "literal", "value": 1}
              ]
            },
            " and position() <= ",
            {
              "op": "add",
              "args": [
                {"op": "value", "xpath": "@First_x0020_Device_x0020_Entry", "dataType": "integer"},
                {"op": "value", "xpath": "@Number_x0020_Of_x0020_Devices", "dataType": "integer"}
              ]
            },
            "]"
          ]
        },
        "expression": {
          "op": "sum",
          "args": [
            {
              "op": "map",
              "xpathExpression": {
                "op": "concat",
                "args": [
                  "//B023_PNT/Record[position() >= ",
                  {
                    "op": "add",
                    "args": [
                      {"op": "value", "xpath": "./Device_x0020_Configuration/Record/@First_x0020_Point_x0020_Record", "dataType": "integer"},
                      {"op": "literal", "value": 1}
                    ]
                  },
                  " and position() <= ",
                  {
                    "op": "add",
                    "args": [
                      {"op": "value", "xpath": "./Device_x0020_Configuration/Record/@First_x0020_Point_x0020_Record", "dataType": "integer"},
                      {"op": "value", "xpath": "./Device_x0020_Configuration/Record/@Number_x0020_of_x0020_Point_x0020_Records", "dataType": "integer"}
                    ]
                  },
                  " and @DCA_x0020_Object_x0020_Type='Analog Input 16']"
                ]
              },
              "expression": {
                "op": "value",
                "xpath": "@Number_x0020_Of_x0020_Device_x0020_Points",
                "dataType": "integer"
              }
            }
          ]
        }
      }
    ]
  },
  "value": 0,
  "operator": ">="
}
```

This complex example:
1. Iterates through each DCA CONFIGURATION record
2. Uses mapping attributes to find related DEVICE CONFIGURATION records
3. Uses mapping attributes to find related DEVICE POINT MAP records
4. Filters for "Analog Input 16" type records
5. Sums the point counts for each DCA record individually
6. Returns per-node PASS/FAIL results

### Result Structure

Returns a `ValidationResult` with:
- Overall PASS/FAIL status for the rule
- `node_results` array containing per-node results:
  - `node_index`: 0-based index
  - `node_xpath`: XPath to the specific node
  - `actual_value`: Value extracted from the node
  - `expected_value`: Expected value for comparison
  - `status`: "pass" or "fail" for this node
  - `message`: Status message for this node

### Use Case

Perfect for scenarios where you need to:
- Validate each record in a series individually
- Get detailed per-node PASS/FAIL results
- Identify which specific nodes fail validation
- Use complex mapping logic per node

---

## 🟢 🔟 Tips for Interpreters
When evaluating map, switch XPath context to each node before evaluating expression.

Be careful with relative XPath queries inside the expression.

All other operations (sum, average, count) expect scalar or array inputs.

For `nodeValidation`, ensure proper context switching when evaluating `nodeValueExpression` and `expectedValueExpression` for each node.


