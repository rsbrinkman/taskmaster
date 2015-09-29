$.fn.clickToEdit = function(options) {
  options = $.extend({
    validate: function() { return true; },
    success: function() {},
    inputType: 'text',
    displayElement: 'div',
    cancelOnBlur: true,
    choices: []
  }, options);

  function process($editable, $display) {
    if(options.validate($editable)) {
      options.success($editable);
      $display.text($editable.val());
    }

    reset($editable, $display);
  }

  function reset($editable, $display) {
    $editable.hide();
    $display.show();
  }

  return this.each(function() {
    var $this = $(this),
        text = $this.text(),
        $display = $('<' + options.displayElement + ' class="editable-display">' +
                     text + '</' + options.displayElement + '>'),
        $editable;

    if(options.inputType === 'select') {
      $editable = $('<select>');
      $editable.append($('<option disabled>'))
      _.each(options.choices, function(choice) {
        $editable.append($('<option value="' + choice + '">' + choice + '</option>'));
      });
    } else {
      $editable = $('<input type="' + options.inputType  + '">');
      $editable.addClass('form-control');
    }

    $editable.addClass('editable').hide();

    $display.on('click', function(event) {
      // Hide any other open editing fields
      $('.editable').hide();
      $('.editable-display').show();

      $display.hide();

      if(options.inputType === 'select') {
        var $existingOption = $editable.find('option[value="' + $display.text() + '"]'),
            $disabledOption = $editable.find('option[disabled]');

        if ($existingOption.length) {
          $disabledOption.hide();
          $existingOption.prop('selected', true);
        } else {
          $disabledOption.show();
          $disabledOption.prop('selected', true);
        }
      } else {
        $editable.val($display.text());
      }
      $editable.show().focus();
    });

    if(options.inputType === 'select') {
      $editable.on('change', function(event) {
        process($editable, $display);
      });
    } else {
      $editable.on('keypress', function(event) {
        if (event.keyCode === 13) {
          process($editable, $display);
        } else if (event.keyCode === 27) {
          reset($editable, $display);
        }
      });
    }

    $editable.on('blur', function(event) {
      if(options.cancelOnBlur) {
        reset($editable, $display);
      } else {
        process($editable, $display);
      }
    });

    $this.text('').append($display, $editable);
  });
};
