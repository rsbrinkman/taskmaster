$(function() {
  $('.project-settings-name.permitted').clickToEdit({
    inputType: 'text',
    displayElement: 'h3',
    success: function($editable) {
      $.ajax({
        type: 'PUT',
        url: '/org/' + STATE.org.id + '/name',
        data: {
          value: $editable.val()
        },
        success: function() {
        }
      });
    }
  });

  $('.project-settings-level.permitted').clickToEdit({
    inputType: 'select',
    displayElement: 'strong',
    choices: STATE.all_levels,
    success: function($editable) {
      $.ajax({
        type: 'PUT',
        url: '/org/' + STATE.org.id + '/level',
        data: {
          value: $editable.val()
        },
        success: function() {
          window.location.reload();
        }
      });
    }
  });

  $('#confirm-project-leave').on('click', function(event) {
      $.ajax({
        type: 'DELETE',
        url: '/org/' + STATE.org.id + '/user/' + STATE.user.id + '/',
        success: function() {
          window.location = "/admin";
        }
      });
  });

  $('#confirm-project-delete').on('click', function(event) {
      $.ajax({
        type: 'DELETE',
        url: '/org/' + STATE.org.id,
        success: function() {
          window.location = "/admin";
        }
      });
  });
});
