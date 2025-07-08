# Convention: Capitalized Class Fields in Python

**ID:** CONVENTION_Capitalized_Class_Fields  
**SCOPE:** Backend (Python)  
**STATUS:** Enforced  
**APPLIES_TO:** All classes in the domain, application, and infrastructure layers  
**ENFORCED_BY:** Code review, static analysis (`pylint` custom rules), IDE templates

---

## 📌 RULE

> **All class fields (instance variables) MUST be named using ALL_CAPS format**.  
> This applies to fields defined in `__init__`, `dataclass` attributes, and dynamically assigned instance fields.

---

### ✅ GOOD_EXAMPLE

```python
class User:
    def __init__(self, user_id: int, email: str):
        self.USER_ID = user_id
        self.EMAIL = email
