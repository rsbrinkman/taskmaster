$(function() {
  $('.user-role-container.permitted').clickToEdit({
    inputType: 'select',
    choices: STATE.user.lte_roles,
    success: function($editable) {
      var userId = $editable.parents('tr').data('user-id'),
          role = $editable.val();

      $.ajax({
        type: 'PUT',
        url: '/org/' + STATE.org.id + '/user/' + userId + '/role/' + role + '/',
        success: function() {
          window.location.reload();
        }
      });
    }
  });

  $('.invite-user').on('submit', function(event) {
    event.stopPropagation();
    event.preventDefault();

    var email = $('.invite-user-email').val(),
        role = $('.invite-user-role').val();

    $.ajax({
      type: 'POST',
      url: '/org/' + STATE.org.id + '/user/' + email + '/',
      data: {
        role: role
      },
      success: function() {
        window.location.reload();
      }
    });
  });

  function deleteUser(username) {
    $.ajax({
      type: 'DELETE',
      url: '/org/' + STATE.org.id + '/user/' + username + '/',
      success: function() {
        window.location.reload();
      }
    });
  }

  $('.cancel-invite').click(function(event) {
    var email = $(this).parents('tr').find('.pending-email').text();
    deleteUser(email);
  });

  $('.kick-user').click(function(event) {
    var userId = $(this).parents('tr').data('user-id');
    deleteUser(userId);
  });
});
