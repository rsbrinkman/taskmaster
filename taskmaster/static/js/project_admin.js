$(function() {
  $('#settings').html(TEMPLATES['settings'](STATE.orgs, STATE.org, STATE.users, STATE.user));
  $("#project-admin").addClass('selected');
});
