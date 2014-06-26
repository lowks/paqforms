# PaqForms4

Locale awared forms with bootstrap widgets

## Installation

pip install git+https://github.com/ivan-kleshnin/paqforms

## FAQ

Q: Is there any difference between
`form.value['foo']`
and
`form.fields['foo'].value`

A: Yes. The `form.value` always builds on `model` object so fields which are
not user-defined in `model` can be impossible to set in some ORM / ODM. As an option,
they may be available before saving and not available after it. It's impossible
to predict all behavior cases. 

So if you've defined one field only in Form and that field has nothing to deal with Model
(captcha being a good example) it's better to check the value via 
`form.fields['foo'].value` 
than 
`form.value['foo']`
