# PaqForms4

Locale awared forms with bootstrap widgets

## Differences from WTForms

- Python3 only!
- Locale-based parsing and formatting. Your data, numbers and so are handled encounting
locale value, not tricky separator arguments.
- Inbuilt Bootstrap3 widgets. You don't have to write and test your own set of macros.
- Flexibility. Forms apply and work with generic python values (request multidicts should be converted
by hand or via additional binding packages, see `flask_paqforms` for example).
Therefore you can use form declarations to work with JSON data.
- Arguably cleaner code, stricter usage of variable names and separation of concerns.
- Single validation phase (at construction time. No confusing `pre-validate`, `conversion-validate` and `post-validate`
phases.
- Object-based and functional value conversions with ability to pipe, map and filter convertors.
For example you can split and trim textarea rows and treat them as list with pure
declarative definitions.
- Translations are at barely minimum (`en` and `ru` for now).

## Installation

`$ pip install --upgrade git+https://github.com/ivan-kleshnin/paqforms4`

## FAQ

Q: Is there any difference between `form.value['foo']` and `form.fields['foo'].value`

A: Yes. The `form.value` always builds on `model` object so fields which are
not user-defined in `model` can be impossible to set in some ORM / ODM. As an option,
they may be available before saving and not available after it. It's impossible
to predict all behavior cases.

So if you've defined one field only in Form and that field has nothing to deal with Model
(captcha being a good example) it's better to check the value via
`form.fields['foo'].value` than `form.value['foo']`
