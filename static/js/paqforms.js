'use strict';

window.pageHandlers = window.pageHandlers || [];

// Handle `FieldFieldidget`
window.pageHandlers.push(function($target) {
    var $fields = $target.find('[data-widget$=FieldField]'); // TODO: $groups?
    if ($fields.length) {
        $fields.each(function () {
            var $field = $(this);
            $field.find("button[data-action=add]").click(function (event) {
                var counter = $field.data('counter') + 1;
                $field.data('counter', counter);
                var $prototype = $field.find("[data-tag=prototype]").clone(true, true);
                $prototype.find(':disabled').removeAttr('disabled');
                $prototype.find('[id$=-0]').each(function () {
                    $(this).attr('id', $(this).attr('id').slice(0, -1) + counter.toString());
                });
                $prototype.find('[name$=-0]').each(function () {
                    $(this).attr('name', $(this).attr('name').slice(0, -1) + counter.toString());
                });
                $prototype.find('[data-name$=-0]').each(function () {
                    $(this).attr('data-name', $(this).attr('data-name').slice(0, -1) + counter.toString());
                });
                $prototype.find('[for$=-0]').each(function () {
                    $(this).attr('for', $(this).attr('for').slice(0, -1) + counter.toString());
                });
                $prototype.attr('data-tag', 'item');
                var $holder = $field.find("[data-tag='holder']");
                $holder.append($prototype);
            });
            $field.find("button[data-action=remove]").click(function (event) {
                var $row = $(this).closest('.row');
                $row.remove();
            });
        });
    }
});

// Handle `MultiCheckboxv`
window.pageHandlers.push(function($target) {
    var $fields = $target.find('[data-widget$=MultiCheckbox]'); // TODO: $groups?
    if ($fields.length) {
        $fields.each(function() {
            var $toggler = $(this).find('[data-tag=toggler]');
            $toggler.change(function () {
                $(this).closest('fieldset')
                .find("input[type='checkbox'][name]")
                .prop('checked', this.checked).change();
            });
        });
    }
});

// Handle `AccessWidget`
window.pageHandlers.push(function($target) {
    var $fields = $target.find('[data-widget$=Access]'); // TODO: $groups?
    if ($fields.length) {
        var render = function render($field, $a) {
            var name = $field.data('name');
            var id = $field.attr('id').replace(/^group-/, '');
            var accessLevel = $a.data('access');
            var iconClass = $a.find('span').attr('class');

            var $control = $field.find('[name=' + name + ']');
            var $li = $a.parent();
            var $ul = $li.parent();
            var $dropdownToggle = $ul.parent().find('.dropdown-toggle');
            var $accessIcon = $($dropdownToggle.find('span')[0]);

            $ul.find('li[class=active]').removeClass('active');
            $li.addClass('active');
            $control.val(accessLevel);
            $accessIcon.attr('class', iconClass);
        };

        $fields.each(function() {
            var $field = $(this);
            var $activeA = $field.find('.dropdown-menu > li[class=active] > a');
            var $allA = $field.find('.dropdown-menu > li > a');
            render($field, $activeA);
            $allA.click(function() {
                event.preventDefault();
                render($field, $(this));
            });
        });
    }
});

// Handle `Filter***Widget`
window.pageHandlers.push(function($target) {
    var $fields = $target.find('[data-widget^=Filter]'); // TODO: $groups?
    if ($fields.length) {
        var render = function render($field) {
            var $commandField = $field.find('[data-name$=command]');
            var $queryFields = $field.find('[data-name]:not([data-name$=command])');
            var commandName = $commandField.data('name');
            var $commandControl = $commandField.find('[name="' + commandName + '"]');
            var queryName = commandName.slice(0, commandName.lastIndexOf('.')) + '.' + $commandControl.val();
            var $fieldToShow = $queryFields.filter('[data-name="' + queryName + '"]');
            var $fieldToHide = $queryFields.filter(':not(.hidden)');
            $fieldToShow.removeClass('hidden');
            $fieldToShow.find('.form-group.hidden').removeClass('hidden');
            $fieldToHide.addClass('hidden');
        };

        $fields.each(function() {
            var $field = $(this);
            var $commandField = $field.find('[data-name$=command]');
            render($field);
            $commandField.change(function() {
                render($field);
            });
        });
    }
});
