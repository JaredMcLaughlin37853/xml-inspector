# XML Inspector DSL Training Manual

A comprehensive guide to implementing Domain Specific Language (DSL) validation rules for XML inspection.

## Table of Contents

1. [Introduction](#introduction)
2. [Basic Document Structure](#basic-document-structure)
3. [Validation Rule Types](#validation-rule-types)
4. [Expression System](#expression-system)
5. [Basic Operations](#basic-operations)
6. [Advanced Operations](#advanced-operations)
7. [Conditional Logic](#conditional-logic)
8. [Dynamic XPath](#dynamic-xpath)
9. [Map Operations](#map-operations)
10. [Complete Examples](#complete-examples)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Introduction

The XML Inspector DSL (Domain Specific Language) provides a powerful, expression-based system for validating XML documents. Unlike simple value matching, the DSL allows you to:

- Perform calculations and aggregations
- Apply complex logical conditions
- Dynamically construct XPath queries
- Iterate over XML nodes with custom expressions
- Build sophisticated validation workflows

---

## Basic Document Structure

Every DSL validation document follows this structure:

```json
{
  "validationSettings": [
    {
      "id": "unique_rule_identifier",
      "description": "Human-readable description",
      "type": "validation_rule_type",
      "severity": "error|warning|info",
      "expression": { /* expression object */ },
      /* additional rule-specific fields */
    }
  ]
}
```

### Required Fields

- **id**: Unique identifier for the rule (string)
- **description**: Human-readable explanation (string)
- **type**: Type of validation rule (see types below)
- **severity**: Impact level (`error`, `warning`, `info`)

---

## Validation Rule Types

### 1. Existence Rules

Check if an expression result exists or is truthy.

```json
{
  "id": "check_items_exist",
  "description": "Verify that items are present in the document",
  "type": "existence",
  "severity": "error",
  "expression": {
    "op": "count",
    "xpath": "//Item"
  }
}
```

### 2. Pattern Rules

Match expression results against regular expressions.

```json
{
  "id": "validate_email_format",
  "description": "Email must be in valid format",
  "type": "pattern",
  "severity": "error",
  "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
  "expression": {
    "op": "value",
    "xpath": "//contact/email/text()"
  }
}
```

### 3. Range Rules

Validate that expression results fall within specified bounds.

```json
{
  "id": "validate_age_range",
  "description": "Age must be between 18 and 65",
  "type": "range",
  "severity": "warning",
  "minValue": "18",
  "maxValue": "65",
  "dataType": "integer",
  "expression": {
    "op": "value",
    "xpath": "//person/@age",
    "dataType": "integer"
  }
}
```

### 4. Comparison Rules

Compare expression results with fixed values.

```json
{
  "id": "minimum_items",
  "description": "Must have at least 5 items",
  "type": "comparison",
  "severity": "error",
  "operator": ">=",
  "value": 5,
  "expression": {
    "op": "count",
    "xpath": "//Item"
  }
}
```

### 5. Computed Comparison Rules

Compare two expressions or use between operations.

```json
{
  "id": "total_vs_sum",
  "description": "Total field must equal sum of line items",
  "type": "computedComparison",
  "severity": "error",
  "comparison": {
    "operator": "==",
    "leftExpression": {
      "op": "value",
      "xpath": "//order/@total",
      "dataType": "decimal"
    },
    "rightExpression": {
      "op": "sum",
      "xpath": "//lineItem/@amount",
      "dataType": "decimal"
    }
  }
}
```

---

## Expression System

Expressions are the core of the DSL, allowing you to compute values from XML data.

### Basic Expression Structure

```json
{
  "op": "operation_name",
  "args": [/* array of arguments */],
  "xpath": "//xpath/expression",
  "xpathExpression": {/* dynamic xpath expression */},
  "expression": {/* sub-expression for map operations */},
  "value": "literal_value",
  "dataType": "string|integer|decimal|date"
}
```

### Data Types

- **string**: Text values (default)
- **integer**: Whole numbers
- **decimal**: Floating-point numbers
- **date**: ISO 8601 date strings

---

## Basic Operations

### count
Count nodes matching an XPath expression.

```json
{
  "op": "count",
  "xpath": "//Product[@category='Electronics']"
}
```

### sum
Sum numeric values from nodes or expression results.

```json
{
  "op": "sum",
  "xpath": "//Item/@price",
  "dataType": "decimal"
}
```

### average
Calculate average of numeric values.

```json
{
  "op": "average",
  "xpath": "//Student/@grade",
  "dataType": "decimal"
}
```

### value
Extract a single value from XML.

```json
{
  "op": "value",
  "xpath": "//Order/@id"
}
```

### literal
Use a constant value.

```json
{
  "op": "literal",
  "value": 100,
  "dataType": "integer"
}
```

---

## Advanced Operations

### Arithmetic Operations

```json
{
  "op": "add",
  "args": [
    {"op": "value", "xpath": "//tax", "dataType": "decimal"},
    {"op": "value", "xpath": "//shipping", "dataType": "decimal"}
  ]
}
```

```json
{
  "op": "multiply",
  "args": [
    {"op": "value", "xpath": "//quantity", "dataType": "integer"},
    {"op": "value", "xpath": "//unitPrice", "dataType": "decimal"}
  ]
}
```

### String Operations

```json
{
  "op": "concat",
  "args": [
    {"op": "value", "xpath": "//firstName/text()"},
    " ",
    {"op": "value", "xpath": "//lastName/text()"}
  ]
}
```

### Comparison Operations

```json
{
  "op": ">",
  "args": [
    {"op": "value", "xpath": "//score", "dataType": "integer"},
    {"op": "literal", "value": 80}
  ]
}
```

---

## Conditional Logic

### if Statements

```json
{
  "op": "if",
  "args": [
    {
      "op": ">",
      "args": [
        {"op": "value", "xpath": "//age", "dataType": "integer"},
        {"op": "literal", "value": 18}
      ]
    },
    {"op": "literal", "value": "Adult"},
    {"op": "literal", "value": "Minor"}
  ]
}
```

### Logical Operations

```json
{
  "op": "and",
  "args": [
    {
      "op": ">=",
      "args": [
        {"op": "value", "xpath": "//score", "dataType": "integer"},
        {"op": "literal", "value": 60}
      ]
    },
    {
      "op": "==",
      "args": [
        {"op": "value", "xpath": "//status"},
        {"op": "literal", "value": "active"}
      ]
    }
  ]
}
```

---

## Dynamic XPath

Build XPath expressions dynamically using expression results.

### Example: Dynamic Attribute Matching

```json
{
  "id": "dynamic_category_count",
  "description": "Count items in dynamically determined category",
  "type": "comparison",
  "severity": "info",
  "operator": ">",
  "value": 0,
  "expression": {
    "op": "count",
    "xpathExpression": {
      "op": "concat",
      "args": [
        "//Item[@category='",
        {"op": "value", "xpath": "//Order/@preferredCategory"},
        "']"
      ]
    }
  }
}
```

### Example: Dynamic Index Selection

```json
{
  "op": "value",
  "xpathExpression": {
    "op": "concat",
    "args": [
      "//Items/Item[",
      {"op": "value", "xpath": "//Config/@selectedIndex"},
      "]/@name"
    ]
  }
}
```

---

## Map Operations

The `map` operation iterates over XML nodes and applies an expression to each one.

### Basic Map Example

```json
{
  "op": "map",
  "xpath": "//LineItem",
  "expression": {
    "op": "multiply",
    "args": [
      {"op": "value", "xpath": "@quantity", "dataType": "decimal"},
      {"op": "value", "xpath": "@unitPrice", "dataType": "decimal"}
    ]
  }
}
```

### Map with Sum

```json
{
  "op": "sum",
  "args": [
    {
      "op": "map",
      "xpath": "//Product",
      "expression": {
        "op": "if",
        "args": [
          {
            "op": "==",
            "args": [
              {"op": "value", "xpath": "@onSale"},
              {"op": "literal", "value": "true"}
            ]
          },
          {
            "op": "multiply",
            "args": [
              {"op": "value", "xpath": "@price", "dataType": "decimal"},
              {"op": "literal", "value": 0.8}
            ]
          },
          {"op": "value", "xpath": "@price", "dataType": "decimal"}
        ]
      }
    }
  ]
}
```

---

## Complete Examples

### Example 1: E-commerce Order Validation

```json
{
  "validationSettings": [
    {
      "id": "order_has_items",
      "description": "Order must contain at least one item",
      "type": "existence",
      "severity": "error",
      "expression": {
        "op": "count",
        "xpath": "//Order/Items/Item"
      }
    },
    {
      "id": "valid_customer_email",
      "description": "Customer email must be in valid format",
      "type": "pattern",
      "severity": "error",
      "pattern": "^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$",
      "expression": {
        "op": "value",
        "xpath": "//Order/Customer/Email/text()"
      }
    },
    {
      "id": "reasonable_item_count",
      "description": "Order should have between 1 and 50 items",
      "type": "range",
      "severity": "warning",
      "minValue": "1",
      "maxValue": "50",
      "dataType": "integer",
      "expression": {
        "op": "count",
        "xpath": "//Order/Items/Item"
      }
    },
    {
      "id": "minimum_order_value",
      "description": "Order total must be at least $10",
      "type": "comparison",
      "severity": "error",
      "operator": ">=",
      "value": 10.00,
      "expression": {
        "op": "sum",
        "args": [
          {
            "op": "map",
            "xpath": "//Order/Items/Item",
            "expression": {
              "op": "multiply",
              "args": [
                {"op": "value", "xpath": "@quantity", "dataType": "integer"},
                {"op": "value", "xpath": "@unitPrice", "dataType": "decimal"}
              ]
            }
          }
        ]
      }
    },
    {
      "id": "total_matches_calculation",
      "description": "Order total must match sum of line items plus tax",
      "type": "computedComparison",
      "severity": "error",
      "comparison": {
        "operator": "==",
        "leftExpression": {
          "op": "value",
          "xpath": "//Order/@total",
          "dataType": "decimal"
        },
        "rightExpression": {
          "op": "add",
          "args": [
            {
              "op": "sum",
              "args": [
                {
                  "op": "map",
                  "xpath": "//Order/Items/Item",
                  "expression": {
                    "op": "multiply",
                    "args": [
                      {"op": "value", "xpath": "@quantity", "dataType": "integer"},
                      {"op": "value", "xpath": "@unitPrice", "dataType": "decimal"}
                    ]
                  }
                }
              ]
            },
            {"op": "value", "xpath": "//Order/@tax", "dataType": "decimal"}
          ]
        }
      }
    }
  ]
}
```

### Example 2: Student Grade Validation

```json
{
  "validationSettings": [
    {
      "id": "student_has_grades",
      "description": "Student must have at least one grade recorded",
      "type": "existence",
      "severity": "error",
      "expression": {
        "op": "count",
        "xpath": "//Student/Grades/Grade"
      }
    },
    {
      "id": "valid_grade_range",
      "description": "All grades must be between 0 and 100",
      "type": "range",
      "severity": "error",
      "minValue": "0",
      "maxValue": "100",
      "dataType": "decimal",
      "expression": {
        "op": "value",
        "xpath": "//Student/Grades/Grade[1]/@score",
        "dataType": "decimal"
      }
    },
    {
      "id": "gpa_calculation",
      "description": "GPA must match average of all grades",
      "type": "computedComparison",
      "severity": "error",
      "comparison": {
        "operator": "==",
        "leftExpression": {
          "op": "value",
          "xpath": "//Student/@gpa",
          "dataType": "decimal"
        },
        "rightExpression": {
          "op": "average",
          "xpath": "//Student/Grades/Grade/@score",
          "dataType": "decimal"
        }
      }
    },
    {
      "id": "honor_roll_qualification",
      "description": "Honor roll students must have GPA >= 3.5",
      "type": "computedComparison",
      "severity": "warning",
      "conditions": [
        {
          "type": "attributeEquals",
          "xpath": "//Student",
          "attribute": "honorRoll",
          "value": "true"
        }
      ],
      "comparison": {
        "operator": ">=",
        "leftExpression": {
          "op": "value",
          "xpath": "//Student/@gpa",
          "dataType": "decimal"
        },
        "rightExpression": {
          "op": "literal",
          "value": 3.5,
          "dataType": "decimal"
        }
      }
    }
  ]
}
```

### Example 3: Financial Report Validation

```json
{
  "validationSettings": [
    {
      "id": "revenue_streams_exist",
      "description": "Report must contain revenue data",
      "type": "existence",
      "severity": "error",
      "expression": {
        "op": "count",
        "xpath": "//FinancialReport/Revenue/Stream"
      }
    },
    {
      "id": "positive_total_revenue",
      "description": "Total revenue must be positive",
      "type": "comparison",
      "severity": "error",
      "operator": ">",
      "value": 0,
      "expression": {
        "op": "sum",
        "xpath": "//FinancialReport/Revenue/Stream/@amount",
        "dataType": "decimal"
      }
    },
    {
      "id": "expense_categories_complete",
      "description": "All major expense categories must be present",
      "type": "computedComparison",
      "severity": "warning",
      "comparison": {
        "operator": ">=",
        "leftExpression": {
          "op": "count",
          "xpath": "//FinancialReport/Expenses/Category"
        },
        "rightExpression": {
          "op": "literal",
          "value": 3
        }
      }
    },
    {
      "id": "profit_loss_accuracy",
      "description": "Net profit must equal revenue minus expenses",
      "type": "computedComparison",
      "severity": "error",
      "comparison": {
        "operator": "==",
        "leftExpression": {
          "op": "value",
          "xpath": "//FinancialReport/@netProfit",
          "dataType": "decimal"
        },
        "rightExpression": {
          "op": "subtract",
          "args": [
            {
              "op": "sum",
              "xpath": "//FinancialReport/Revenue/Stream/@amount",
              "dataType": "decimal"
            },
            {
              "op": "sum",
              "xpath": "//FinancialReport/Expenses/Category/@amount",
              "dataType": "decimal"
            }
          ]
        }
      }
    },
    {
      "id": "margin_calculation",
      "description": "Profit margin must be calculated correctly",
      "type": "computedComparison",
      "severity": "warning",
      "comparison": {
        "operator": "==",
        "leftExpression": {
          "op": "value",
          "xpath": "//FinancialReport/@profitMargin",
          "dataType": "decimal"
        },
        "rightExpression": {
          "op": "divide",
          "args": [
            {
              "op": "multiply",
              "args": [
                {
                  "op": "subtract",
                  "args": [
                    {
                      "op": "sum",
                      "xpath": "//FinancialReport/Revenue/Stream/@amount",
                      "dataType": "decimal"
                    },
                    {
                      "op": "sum",
                      "xpath": "//FinancialReport/Expenses/Category/@amount",
                      "dataType": "decimal"
                    }
                  ]
                },
                {"op": "literal", "value": 100}
              ]
            },
            {
              "op": "sum",
              "xpath": "//FinancialReport/Revenue/Stream/@amount",
              "dataType": "decimal"
            }
          ]
        }
      }
    }
  ]
}
```

---

## Best Practices

### 1. Rule Organization

- **Group related rules**: Keep validation rules for the same business domain together
- **Use descriptive IDs**: Make rule IDs self-explanatory (`validate_email_format` vs `rule_001`)
- **Clear descriptions**: Write descriptions that explain the business reason, not just the technical check

### 2. Performance Considerations

- **Minimize XPath complexity**: Simple XPath expressions perform better
- **Use specific paths**: Avoid `//` when you know the exact path
- **Limit map operations**: Maps over large node sets can be expensive

### 3. Expression Design

- **Break complex expressions**: Split complex logic into multiple rules when possible
- **Use appropriate data types**: Specify `dataType` for numeric operations
- **Handle edge cases**: Consider what happens with missing data

### 4. Error Handling

- **Choose appropriate severity levels**:
  - `error`: Critical business rule violations
  - `warning`: Important but non-blocking issues
  - `info`: Informational checks
- **Use conditions wisely**: Apply conditional rules only when necessary

### 5. Testing Strategy

```json
{
  "validationSettings": [
    {
      "id": "test_data_availability",
      "description": "Ensure test data is present before running business rules",
      "type": "existence",
      "severity": "error",
      "expression": {
        "op": "count",
        "xpath": "//TestData/*"
      }
    }
  ]
}
```

---

## Troubleshooting

### Common Issues

#### 1. XPath Returns No Results

```json
// ❌ Problematic
{
  "op": "value",
  "xpath": "//NonExistentElement/@attribute"
}

// ✅ Better with existence check first
{
  "id": "check_element_exists",
  "type": "existence",
  "expression": {
    "op": "count",
    "xpath": "//NonExistentElement"
  }
}
```

#### 2. Type Conversion Errors

```json
// ❌ Problematic - trying to sum text
{
  "op": "sum",
  "xpath": "//Item/@description"
}

// ✅ Better - sum numeric attributes
{
  "op": "sum",
  "xpath": "//Item/@price",
  "dataType": "decimal"
}
```

#### 3. Division by Zero

```json
// ❌ Problematic
{
  "op": "divide",
  "args": [
    {"op": "value", "xpath": "//total"},
    {"op": "count", "xpath": "//items"}
  ]
}

// ✅ Better - check denominator first
{
  "op": "if",
  "args": [
    {
      "op": ">",
      "args": [
        {"op": "count", "xpath": "//items"},
        {"op": "literal", "value": 0}
      ]
    },
    {
      "op": "divide",
      "args": [
        {"op": "value", "xpath": "//total"},
        {"op": "count", "xpath": "//items"}
      ]
    },
    {"op": "literal", "value": 0}
  ]
}
```

### Debugging Tips

1. **Test expressions incrementally**: Start with simple expressions and build complexity
2. **Use existence rules first**: Verify data exists before processing it
3. **Check data types**: Ensure numeric operations use proper data types
4. **Validate XPath expressions**: Test XPath queries independently
5. **Use meaningful descriptions**: Help identify which rules are failing

### Validation Checklist

- [ ] All required fields present (`id`, `description`, `type`, `severity`)
- [ ] XPath expressions are valid
- [ ] Data types specified for numeric operations
- [ ] Conditional logic properly structured
- [ ] Edge cases considered (empty data, division by zero)
- [ ] Rule descriptions are clear and business-focused
- [ ] Appropriate severity levels assigned
- [ ] Performance implications considered for large datasets

---

## Conclusion

The XML Inspector DSL provides a powerful framework for creating sophisticated XML validation rules. By combining basic operations with advanced features like map operations, conditional logic, and dynamic XPath generation, you can create comprehensive validation suites that ensure data quality and business rule compliance.

Start with simple rules and gradually incorporate more advanced features as you become comfortable with the DSL syntax. Remember to test your rules thoroughly and consider performance implications for production use.