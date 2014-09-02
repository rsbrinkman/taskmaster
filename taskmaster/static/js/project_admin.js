$(function() {
  _.each(['users', 'settings'], function(id) {
    $('#' + id).html(TEMPLATES[id]({STATE: STATE}));
  });

  $("#project-admin").addClass('selected');
});
